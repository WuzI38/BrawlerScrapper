from app.src.methods import dbh_init, scrap_single_page, extract_deck_data, add_deck_to_db


def add_recent():
    """
        Scraps most recent data (one day)
    """
    dbh = dbh_init()

    page_num = 1

    while True:
        data_mtgdecks = scrap_single_page(page_number=page_num, mtgdecks=True, limit_days=1)
        if not data_mtgdecks:
            break
        for deck in data_mtgdecks:
            value_list, colors, wins, losses = extract_deck_data(deck)
            add_deck_to_db(dbh, value_list, colors, wins, losses)
        page_num += 1

    data_aetherhub = scrap_single_page(page_number=page_num, mtgdecks=False, limit_days=1)
    if not data_aetherhub:
        return
    for deck in data_aetherhub:
        value_list, colors, wins, losses = extract_deck_data(deck)
        add_deck_to_db(dbh, value_list, colors, wins, losses)

    dbh.disconnect()


def add_test(mtgdecks: bool = True):
    """
        Scraps data from one page only

        Args:
            mtgdecks (int): If True uses mtgdecks as a source (default)
    """
    dbh = dbh_init()

    data = scrap_single_page(page_number=1, mtgdecks=mtgdecks)
    if not data:
        dbh.disconnect()
        return
    for deck in data:
        value_list, colors, wins, losses = extract_deck_data(deck)
        add_deck_to_db(handler=dbh, value_list=value_list, colors=colors,
                       wins=wins, losses=losses, print_info=True)

    dbh.disconnect()


def add_all(mtgdecks: bool, start_page: int = 1):
    """
        Scraps data for as long as it's possible

        Args:
            start_page (int): The initial page number used by the data scrapper
            mtgdecks (bool): If true scraps data from mtgdecks, if false from aetherhub
    """
    dbh = dbh_init()

    txt = "mtgdecks" if mtgdecks else "aetherhub"
    print(f"Processing data for {txt} page {start_page}")

    data = scrap_single_page(page_number=start_page, mtgdecks=mtgdecks)
    if not data:
        dbh.disconnect()
        return
    for deck in data:
        value_list, colors, wins, losses = extract_deck_data(deck)
        add_deck_to_db(handler=dbh, value_list=value_list, colors=colors,
                       wins=wins, losses=losses)

    dbh.disconnect()
