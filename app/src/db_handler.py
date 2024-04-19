import mysql.connector
from app.src.api_handler import get_card_info
from mysql.connector import errorcode
from time import sleep
from configparser import ConfigParser
import os


class DBHandler:
    def __init__(self):
        self._cnx = None
        self._cursor = None

    def connect(self, database: str = '', host: str = 'localhost', user: str = '', password: str = ''):
        """
            Connects to a database

            Args:
                database (str): The name the card database
                host (func): The ip address of the database (or localhost by default)
                user (str): Database username
                password (str): Database password
        """
        if user == '' or password == '' or database == '':
            user, password, database, host = get_database_config()

        self._cnx = mysql.connector.connect(user=user, password=password,
                                            host=host, database=database)
        self._cursor = self._cnx.cursor(buffered=True)

    def insert_new_card(self, card_name: str):
        """
            Inserts a new MTG card to a database

            Args:
                card_name (str): The name of the MTG card
        """
        self._cursor.execute("SELECT * FROM Cards WHERE name = %s", (card_name,))
        card_exists = self._cursor.fetchone()

        if not card_exists:
            card_type, image_url = get_card_info(card_name)
            sleep(0.1)  # Wait for api

            if card_type is not None and image_url is not None:
                try:
                    self._cursor.execute("INSERT INTO Cards (name, type, image) VALUES (%s, %s, %s)",
                                         (card_name, card_type, image_url))
                    self._cnx.commit()
                except mysql.connector.Error as err:
                    print(f'Error: {err}')

    def insert_commander(self, commander_name: str, colors: str, wins: int = 0, losses: int = 0):
        """
            Inserts a new MTG card to a database

            Args:
                commander_name (str): The name of the MTG commander
                colors (str): The colors of the chosen commander
                wins (int): The number of games won by the players playing the chosen commander
                losses (int): The number of games lost by the players playing the chosen commander
        """
        self._cursor.execute("SELECT id FROM Cards WHERE name = %s", (commander_name,))
        commander_id = self._cursor.fetchone()
        if commander_id:
            self._cursor.execute(
                "UPDATE Commanders SET decks = decks + 1, wins = wins + %s, losses = losses + %s WHERE card_id = %s",
                (wins, losses, commander_id[0]))
            self._cnx.commit()
        else:
            print(f"Trying to insert {commander_name}")
            self.insert_new_card(commander_name)
            self._cursor.execute("SELECT id FROM Cards WHERE name = %s", (commander_name,))
            card_id = self._cursor.fetchone()
            if card_id:
                self._cursor.execute("INSERT INTO Commanders (card_id, colors, wins, losses) VALUES (%s, %s, %s, %s)",
                                     (card_id[0], colors, wins, losses))
                self._cnx.commit()

    def add_card_to_commander(self, card_name: str, commander_name: str):
        """
            Assigns a card to the chosen commander

            Args:
                card_name (str): The name of the MTG card
                commander_name (str): The name of the MTG commander
        """
        self._cursor.execute("SELECT id FROM Cards WHERE name = %s", (card_name,))
        card_id = self._cursor.fetchone()
        self._cursor.execute("SELECT id FROM Commanders WHERE card_id = (SELECT id FROM Cards WHERE name = %s)",
                             (commander_name,))
        commander_id = self._cursor.fetchone()
        if card_id and commander_id:
            try:
                self._cursor.execute('INSERT INTO Decks (commander_id, card_id) VALUES (%s, %s)',
                                     (commander_id[0], card_id[0]))
                self._cnx.commit()
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_DUP_ENTRY:
                    self._cursor.execute(
                        "UPDATE Decks SET card_count = card_count + 1 WHERE commander_id = %s AND card_id = %s",
                        (commander_id[0], card_id[0]))
                    self._cnx.commit()

    def get_popular_commanders(self, limit: int) -> list:
        """
            Returns the top X popular commanders

            Args:
                limit (int): The number of commanders to return
        """
        self._cursor.execute(
            "SELECT c.name, c.image FROM Commanders com JOIN Cards c ON com.card_id = c.id "
            "ORDER BY com.decks DESC LIMIT %s",
            (limit,))
        commanders = self._cursor.fetchall()
        return commanders

    def get_best_winrate_commanders(self, limit: int) -> list:
        """
            Returns the top X commanders with the best win rate

            Args:
                limit (int): The number of commanders to return
        """
        self._cursor.execute(
            "SELECT c.name, c.image "
            "FROM Commanders com JOIN Cards c ON com.card_id = c.id "
            "WHERE com.wins > 0 AND com.losses > 0 "
            "ORDER BY com.wins/com.losses DESC LIMIT %s",
            (limit,))
        commanders = self._cursor.fetchall()
        return commanders

    def get_popular_cards(self, limit: int) -> list:
        """
            Returns the top X popular cards

            Args:
                limit (int): The number of cards to return
        """
        self._cursor.execute(
            "SELECT c.name, c.image FROM Decks d JOIN Cards c ON d.card_id = c.id GROUP BY c.id "
            "ORDER BY SUM(d.card_count) DESC LIMIT %s",
            (limit,))
        cards = self._cursor.fetchall()
        return cards

    def get_commanders_by_color(self, colors: str) -> list:
        """
            Returns all commanders of a given color

            Args:
                colors (str): The colors of the commanders to return
        """
        self._cursor.execute(
            "SELECT com.id, c.name, c.image FROM Commanders com JOIN Cards c ON "
            "com.card_id = c.id WHERE com.colors = %s ORDER BY com.decks DESC",
            (colors,))
        commanders = self._cursor.fetchall()
        return commanders

    def get_commander_cards(self, commander_id: int, card_type: str, percent: float, low: int, high: int) -> list:
        """
            Returns a certain percentage of cards of a given type for a given commander,
            but not less than a specified lower limit and not more than a specified upper limit.

            Args:
                commander_id (int): The ID of the commander
                card_type (str): The type of the cards
                percent (float): The percentage of cards to return
                low (int): The minimum number of cards to return
                high (int): The maximum number of cards to return
        """
        # Get all cards of the given type for the given commander
        self._cursor.execute(
            "SELECT c.name, c.image FROM Decks d JOIN Cards c ON d.card_id = c.id "
            "WHERE d.commander_id = %s AND c.type = %s ORDER BY d.card_count DESC",
            (commander_id, card_type))
        cards = self._cursor.fetchall()

        low = max(low, 0)
        high = min(high, 50)
        if not 0 < percent <= 1:
            percent = 0.6

        cl = len(cards)

        num_cards = min(cl, max(min(int(cl * percent), high), low))

        return cards[:num_cards]

    def get_card_types(self) -> list:
        """

        Returns: List of legal card types

        """
        self._cursor.execute("SELECT type FROM cards GROUP BY type")
        types = self._cursor.fetchall()

        types = [t[0] for t in types]

        return types

    def get_colors(self) -> list:
        """

        Returns: List of possible color combinations

        """
        self._cursor.execute("SELECT colors FROM commanders GROUP BY colors")
        colors = self._cursor.fetchall()

        colors = [t[0] for t in colors]
        letter_order = {'w': '1', 'u': '2', 'b': '3', 'r': '4', 'g': '5', 'c': '6'}
        return sorted(colors, key=lambda x: (len(x), int(''.join(letter_order[ch] for ch in x))))

    def cursor_set(self) -> bool:
        return self._cursor is not None

    def empty_db(self):
        """
            Removes everything from database
        """
        try:
            self._cursor.execute("DELETE FROM Decks WHERE commander_id > 0")
            self._cursor.execute("DELETE FROM Commanders WHERE id > 0")
            self._cursor.execute("DELETE FROM Cards WHERE id > 0")
            self._cnx.commit()
        except Exception as e:
            print(f"Cannot reset database: {e}")

    def disconnect(self):
        self._cnx.close()


def get_database_config() -> tuple:
    """
        Sets up default connection config
    """
    default_config = ('root', 'root', 'Brawler', 'localhost')
    try:
        config = ConfigParser()
        cwd = os.getcwd()

        if os.path.basename(cwd) == 'database':
            config_path = os.path.join(cwd, '..', '..', 'config', 'config.ini')
        else:
            config_path = os.path.join(cwd, 'config', 'config.ini')

        config_path = os.path.normpath(config_path)

        config.read(config_path)

        if 'database' in config:
            user = config['database'].get('user', 'root')
            password = config['database'].get('password', 'root')
            name = config['database'].get('name', 'Brawler')
            host = config['database'].get('host', 'localhost')
            return user, password, name, host
    except FileNotFoundError:
        print("Config file not found")
    except KeyError:
        print("Wrong config key")

    print('xd')

    return default_config
