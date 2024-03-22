from url_scrapper import *
from app.src.db_handler import DBHandler
from configparser import ConfigParser
from traceback import format_exc


def add_decks(handler: DBHandler, host: str = 'localhost', mtgdecks: bool = True,
              limit_days: int = -1, start_page: int = 1, print_page: bool = False):

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
    dbh = DBHandler()

    config = ConfigParser()
    config.read('config.ini')

    database_name = config['database']['name']

    dbh.connect(database=database_name)

    return dbh


def add_recent(host: str = 'localhost'):
    dbh = dbh_init()

    add_decks(handler=dbh, host=host, mtgdecks=True, limit_days=1)
    add_decks(handler=dbh, host=host, mtgdecks=False, limit_days=1)


def add_all(host: str = 'localhost', start_page: int = 1):
    dbh = dbh_init()

    add_decks(handler=dbh, host=host, mtgdecks=True, start_page=start_page, print_page=True)
    add_decks(handler=dbh, host=host, mtgdecks=False, start_page=start_page, print_page=True)


def add_test(host: str = 'localhost', mtgdecks: bool = True):
    dbh = dbh_init()

    add_decks(handler=dbh, host=host, mtgdecks=mtgdecks, limit_days=1)
