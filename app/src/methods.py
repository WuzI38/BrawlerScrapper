from url_scrapper import *
from app.src.db_handler import DBHandler
from configparser import ConfigParser
from traceback import format_exc


def add_decks(handler: DBHandler, host: str = 'localhost', mtgdecks: bool = True,
              limit_days: int = -1, start_page: int = 1, print_page: bool = False):
    """
        Adds multiple decks to the database

        Args:
            handler (DBHandler): The handler for the database connection
            host (str): The ip address of the database (or localhost by default)
            mtgdecks (bool): True if the data come from mtg decks
            limit_days (int): Days between the day the deck was published and today
            start_page (int): The initial page number used by the data scrapper
            print_page (bool): If True prints page number
    """
    if not handler.cursor_set():
        handler = DBHandler()
        handler.connect(database='Brawler', host=host)

    page = start_page
    finished = False

    while not finished:
        if mtgdecks:
            if limit_days > 0:
                data = get_deck_data_mtgdecks(page_number=page, limit_days=limit_days)
            else:
                data = get_deck_data_mtgdecks(page_number=page)
        else:
            if limit_days > 0:
                data = get_deck_data_aetherhub(page_number=page, limit_days=limit_days)
            else:
                data = get_deck_data_aetherhub(page_number=page)

        if print_page:
            print(page)
        page += 1

        for deck in data:
            if not data:
                finished = True
                break

            link = deck["Link"]
            colors = deck["Colors"]

            if mtgdecks:
                wins = 0
                losses = 0
                my_dict = get_deck_list_mtgdecks(link)
            else:
                wins = deck["Wins"]
                losses = deck["Loses"]
                my_dict = get_deck_list_aetherhub(link)

            if not my_dict:
                continue

            value_list = list(my_dict.values())

            if len(value_list) == 2 and len(value_list[1]) > 0:
                try:
                    commander_name = value_list[0]
                    handler.insert_commander(commander_name=commander_name, colors=colors, wins=wins, losses=losses)
                    for card in value_list[1]:
                        handler.insert_new_card(card_name=card)
                        handler.add_card_to_commander(card_name=card, commander_name=commander_name)
                except Exception as e:
                    with open('logs.txt', 'a') as f:
                        now = datetime.now()
                        current_time = now.strftime("%d-%m-%Y %H:%M:%S")
                        f.write(f'\n{current_time} - Error occurred: {str(e)}\n')
                        f.write(format_exc())


def dbh_init() -> DBHandler:
    """
        Initializes database connection
    """
    dbh = DBHandler()

    config = ConfigParser()
    config.read('config.ini')

    database_name = config['database']['name']

    dbh.connect(database=database_name)

    return dbh


def add_recent(host: str = 'localhost'):
    """
        Scraps most recent data (one day)

        Args:
            host (str): The ip address of the database (or localhost by default)
    """
    dbh = dbh_init()

    add_decks(handler=dbh, host=host, mtgdecks=True, limit_days=1)
    add_decks(handler=dbh, host=host, mtgdecks=False, limit_days=1)


def add_all(host: str = 'localhost', start_page: int = 1):
    """
        Scraps data for as long as it's possible

        Args:
            host (str): The ip address of the database (or localhost by default)
            start_page (int): The initial page number used by the data scrapper
    """
    dbh = dbh_init()

    add_decks(handler=dbh, host=host, mtgdecks=True, start_page=start_page, print_page=True)
    add_decks(handler=dbh, host=host, mtgdecks=False, start_page=start_page, print_page=True)


def add_test(host: str = 'localhost', mtgdecks: bool = True):
    """
        Scraps data from one page only

        Args:
            host (str): The ip address of the database (or localhost by default)
            mtgdecks (int): If True uses mtgdecks as a source (default)
    """
    dbh = dbh_init()

    add_decks(handler=dbh, host=host, mtgdecks=mtgdecks, limit_days=1, print_page=True)
