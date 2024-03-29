from app.src.url_scrapper import *
from app.src.db_handler import DBHandler, get_database_config
from mysql.connector import InternalError


def scrap_single_page(page_number: int, mtgdecks: bool = True, limit_days: int = -1, custom_page: str = '') -> list:
    """
        Scraps single page from given source

        Args:
            custom_page: (str): Custom page url (mtgdecks only)
            page_number (int): The number of the chosen page
            mtgdecks (bool): If true choose mtgdecks, else choose aetherhub
            limit_days (int): Scraps only data not older than limit_days, if mtgdecks is false max limit is one month
    """
    if mtgdecks:
        if limit_days > 0:
            data = get_deck_data_mtgdecks(page_number=page_number, limit_days=limit_days, custom_page=custom_page)
        else:
            data = get_deck_data_mtgdecks(page_number=page_number, custom_page=custom_page)
    else:
        if limit_days > 0:
            data = get_deck_data_aetherhub(page_number=page_number, limit_days=limit_days)
        else:
            data = get_deck_data_aetherhub(page_number=page_number)

    return data


def extract_deck_data(deck: dict, mtgdecks: bool) -> tuple:
    """
        Extracts deck stats and link to decklist from a dictionary

        Args:
            mtgdecks (bool): True if the link leads to mtgdecks page
            deck (dict): Decks, data stored in dictionary
    """
    if not deck:
        print("Deck data not found")
        return ()

    try:
        link = deck["Link"]
        colors = deck["Colors"]
        wins = deck["Wins"]
        losses = deck["Losses"]
        if mtgdecks:
            my_dict = get_deck_list_mtgdecks(link)
        else:
            my_dict = get_deck_list_aetherhub(link)

        if not my_dict:
            print("Decklist not found")
            return ()
    except KeyError:
        print("Wrong deck key")
        return ()

    value_list = list(my_dict.values())
    return value_list, colors, wins, losses


def add_deck_to_db(handler: DBHandler, value_list: list, colors: str, wins: int, losses: int, print_info=False):
    """
        Adds chosen deck to the database

        Args:
            handler (DBHandler): Database connector
            value_list (list): List containing commander name and the names of every single card
            colors (str): Commander's colors
            wins (int): Matches won by given deck, 0 by default
            losses (int): Matches lost by given deck, 0 by default
            print_info (bool): Prints helpful info if true
    """
    if not handler.cursor_set():
        handler = DBHandler()
        handler.connect()

    if len(value_list) == 2 and len(value_list[1]) > 0:
        try:
            commander_name = value_list[0]
            handler.insert_commander(commander_name=commander_name, colors=colors, wins=wins, losses=losses)
            if print_info:
                print(f'Commander added: {commander_name}')
            for card in value_list[1]:
                handler.insert_new_card(card_name=card)
                handler.add_card_to_commander(card_name=card, commander_name=commander_name)
                if print_info:
                    print(f'Card added: {card}')
        except InternalError:
            print(f"Internal error occurred")
        except Exception as e:
            print(f"Error occurred: {str(e)}")


def dbh_init() -> DBHandler:
    """
        Initializes database connection
    """
    dbh = DBHandler()

    user, password, database_name, host = get_database_config()

    dbh.connect(database=database_name, user=user, password=password, host=host)

    return dbh


def dbh_empty():
    """
        Removes all data from the database
    """
    dbh = dbh_init()
    dbh.empty_db()
    dbh.disconnect()
