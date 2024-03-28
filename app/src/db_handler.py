import mysql.connector
from app.src.api_handler import get_card_info
from mysql.connector import errorcode
from time import sleep
from configparser import ConfigParser


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
            user, password, database, _ = get_database_config()

        self._cnx = mysql.connector.connect(user=user, password=password,
                                            host=host, database=database)
        self._cursor = self._cnx.cursor()

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
        config.read('config/config.ini')

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

    return default_config
