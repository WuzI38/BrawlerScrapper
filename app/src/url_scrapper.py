from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup, Tag


def get_aetherhub_decks(page_number: int) -> str:
    """
        Gets the page containing deck urls from aetherhub

        Args:
            page_number (int): The number of aetherhub deck page
    """
    url = f'https://aetherhub.com/MTGA-Decks/Historic-Brawl/?p={page_number}'
    page = requests.get(url)
    return page.text


def create_aetherhub_deck_list(page_text: str, limit_days: int = -1):
    """
        Creates a list of dictionaries for every commander's deck on a given page

        Args:
            page_text (int): The text of an aetherhub page
            limit_days (int): Days between the day the deck was published and today. Works only for decks not older
            than one month
    """
    soup = BeautifulSoup(page_text, 'html.parser')
    rows = soup.find_all('tr', class_='ae-tbody-deckrow')

    deck_data = []

    try:
        for row in rows:
            if limit_days > 0:
                days = row.find_all('td', class_='text-right')[0].text.split()
                if limit_days == 1:
                    if days[1][0] == 'd' or days[1][0:2] == 'mo' or days[1][0] == 'y':  # Only hour or hours qualified
                        break  # mo added, so that minutes are also included
                elif limit_days == 2:
                    if days[1] == 'days' or days[1][0] == 'm' or days[1][0] == 'y' or days[1][0] == 'h':  # Only day
                        break
                else:
                    if days[1] == 'days' and int(days[0]) > limit_days - 1:  # Only days (in given range)
                        break
                    if days[1][0] == 'm' or days[1][0] == 'y' or days[1][0] == 'h':  # Only days, not hour, month, year
                        break

            deck = dict()
            deck['Link'] = 'https://aetherhub.com' + row.find('a')['href']
            # deck['Name'] = row.find('b').text.replace("'", "'")

            colors = row.find('span', class_='metalist-colors')['data-colors'].split('|')
            color_codes = ['w', 'u', 'b', 'r', 'g', 'c']
            deck['Colors'] = ''.join([color_codes[i] for i, val in enumerate(colors[:-1]) if int(val) > 0])
            if all(int(val) == 0 for val in colors[:-1]) and int(colors[-1]) > 0:
                deck['Colors'] = 'c'

            win_loss = row.find_all('td', class_='text-center')[-1].text.split(': ')[1].split(' - ')
            deck['Wins'] = win_loss[0].split()[0]
            deck['Losses'] = win_loss[1].split()[0]

            deck_data.append(deck)
    except TypeError:
        pass
    except Exception as e:
        print(f'Parsing error occurred: {e.args}')

    return deck_data


def get_deck_data_aetherhub(page_number: int, limit_days: int = -1) -> list:
    """
        Invokes functions for scrapping and organizing the data

        Args:
            page_number (int): The number of mtgdecks deck page
            limit_days (int): Days between the day the deck was published and today
    """
    text = get_aetherhub_decks(page_number)
    return create_aetherhub_deck_list(text, limit_days)


def get_mtgdecks_decks(page_number: int, custom_page: str = '') -> str:
    """
        Gets the page containing deck urls from mtgdecks

        Args:
            custom_page (str): Custom page url
            page_number (int): The number of mtgdecks deck page
    """
    if custom_page == '':
        url = f'https://mtgdecks.net/Historic-Brawl/decklists/page:{page_number}'
    else:
        url = custom_page
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                      'Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
    }
    page = session.get(url, headers=headers)
    return page.text


def create_mtgdecks_deck_list(page_text: str, limit_days: int = -1) -> list:
    """
        Creates a list of dictionaries for every commander's deck on a given page

        Args:
            page_text (int): The text of the mtgdecks page
            limit_days (int): Days between the day the deck was published and today
    """
    soup = BeautifulSoup(page_text, 'html.parser')

    rows = soup.find_all('tr')

    deck_info_list = []

    for row in rows:
        try:
            if limit_days > 0:
                try:
                    date_tag = row.find_all('strong')[2]
                except IndexError:
                    continue
                date_str = date_tag.get_text(strip=True)
                date = datetime.strptime(date_str, '%d-%b-%Y')
                days_ago = datetime.now() - timedelta(days=limit_days)

                if date <= days_ago:
                    break

            deck = dict()

            link = row.find('a')['href']

            if not is_number_after_dash(link):
                continue

            colors = row.find_all('span', {'class': lambda x: x and x.startswith('ms ms-cost ms-')})
            color_dict = {'ms-w': 'w', 'ms-u': 'u', 'ms-b': 'b', 'ms-r': 'r', 'ms-g': 'g', 'ms-c': 'c'}
            found_colors = [color_dict[color['class'][2]] for color in colors]
            color_order = ['w', 'u', 'b', 'r', 'g', 'c']
            colors = ''.join([color for color in color_order if color in found_colors])

            deck['Link'] = f'https://mtgdecks.net{link}'
            deck['Colors'] = colors
            deck['Wins'] = 0
            deck['Losses'] = 0

            deck_info_list.append(deck)
        except TypeError:
            pass
        except Exception as e:
            print(f'Parsing error occurred: {e.args}')

    return deck_info_list


def get_deck_data_mtgdecks(page_number: int, limit_days: int = -1, custom_page: str = '') -> list:
    """
        Invokes functions for scrapping and organizing the data

        Args:
            custom_page (str): Custom page url
            page_number (int): The number of mtgdecks deck page
            limit_days (int): Days between the day the deck was published and today
    """
    text = get_mtgdecks_decks(page_number, custom_page=custom_page)
    return create_mtgdecks_deck_list(text, limit_days)


def get_single_deck_data_aetherhub(deck_url: str) -> str:
    """
        Gets the page containing single deck list (aetherhub)

        Args:
            deck_url (str): The page's url
    """
    page = requests.get(deck_url)
    return page.text


def create_aetherhub_single_deck_dict(page_text: str, replace_arena_only: bool = False) -> dict:
    """
        Creates a dictionary containing deck list from a page text (aetherhub)

        Args:
            page_text (str): The page's text
            replace_arena_only (bool): Transforms arena only names to regular names
    """
    soup = BeautifulSoup(page_text, 'html.parser')

    try:
        first_table = soup.find_all('table')[0]
        h_tag = first_table.find_previous_sibling(lambda tag: tag.name.startswith('h'))
        commander_name = first_table.find('a').text.strip()
        second_table = soup.find_all('table')[1]
    except AttributeError:
        return {}
    except IndexError:
        return {}

    if h_tag is None or 'Commander' not in h_tag.text:
        return {}

    if replace_arena_only:
        commander_name = commander_name.replace("A-", "")

    decklist = []
    rows = second_table.find_all('tr')
    for row in rows:
        try:
            div = row.find('div')
            if div is not None and isinstance(div, Tag):
                div_text = row.find('div').text.strip()
                dts = div_text.split()
                quantity, card_name = dts[0], ' '.join(dts[1:])

                if replace_arena_only:
                    card_name = card_name.replace("A-", "")

                if quantity == '1' and card_name not in ['Forest', 'Plains', 'Mountain', 'Swamp', 'Island',
                                                         'Snow-Covered Forest', 'Snow-Covered Plains',
                                                         'Snow-Covered Mountain',
                                                         'Snow-Covered Swamp', 'Snow-Covered Island']:
                    decklist.append(card_name)
            else:
                continue
        except AttributeError:
            continue

    return {'Commander': commander_name, 'Decklist': decklist}


def get_deck_list_aetherhub(deck_url: str, replace_arena_only: bool = False) -> dict:
    """
        Invokes functions for scrapping and organizing the deck list data

        Args:
            deck_url (int): The page's url
            replace_arena_only (int): Transforms arena only names to regular names
    """
    text = get_single_deck_data_aetherhub(deck_url)
    return create_aetherhub_single_deck_dict(text, replace_arena_only=replace_arena_only)


def get_single_deck_data_mtgdecks(deck_url: str) -> str:
    """
        Gets the page containing single deck list (mtgdecks)

        Args:
            deck_url (str): The page's url
    """
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                      'Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
    }
    page = session.get(deck_url, headers=headers)
    return page.text


def create_mtgdecks_single_deck_dict(page_text: str, replace_arena_only: bool = False) -> dict:
    """
        Creates a dictionary containing deck list from a page text (mtgdecks)

        Args:
            page_text (str): The page's text
            replace_arena_only (bool): Transforms arena only names to regular names
    """
    soup = BeautifulSoup(page_text, 'html.parser')

    try:
        tables = soup.find_all('table')

        sideboard_table = tables[-2]
        sideboard_header = sideboard_table.find('th', class_='type Sideboard')
        sideboard_text = " ".join(sideboard_header.get_text().strip().split())
        commander_name = sideboard_table.find('a').text
    except AttributeError:
        return {}
    except IndexError:
        return {}

    if sideboard_text != 'Sideboard [1]':
        return {}

    if replace_arena_only:
        commander_name = commander_name.replace("A-", "")

    decklist = []
    for table in tables[:-2]:  # Exclude the last two tables
        rows = table.find_all('tr')
        for row in rows:
            try:
                quantity = row.find('span', class_='rarity').next_sibling.strip()
                card_name = row.find('a').text
                if replace_arena_only:
                    card_name = card_name.replace('A-', '')
                if quantity == "1" and card_name not in ['Forest', 'Plains', 'Mountain', 'Swamp', 'Island',
                                                         'Snow-Covered Forest', 'Snow-Covered Plains',
                                                         'Snow-Covered Mountain', 'Snow-Covered Swamp',
                                                         'Snow-Covered Island']:
                    decklist.append(card_name)
            except AttributeError:
                continue

    return {'Commander': commander_name, 'Decklist': decklist}


def get_deck_list_mtgdecks(deck_url: str, replace_arena_only: bool = False) -> dict:
    """
        Invokes functions for scrapping and organizing the deck list data

        Args:
            deck_url (int): The page's url
            replace_arena_only (int): Transforms arena only names to regular names
    """
    text = get_single_deck_data_mtgdecks(deck_url)
    return create_mtgdecks_single_deck_dict(text, replace_arena_only=replace_arena_only)


def is_number_after_dash(url_string: str) -> bool:
    """
        Checks if the url contains commander id

        Args:
            url_string (str): Url of a decklist
    """
    try:
        substring = url_string.rsplit('-', 1)[-1]
        float(substring)
        return True
    except ValueError:
        return False
