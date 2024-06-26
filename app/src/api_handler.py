import requests


def get_api_data(card_name: str, modify_name: bool = False) -> dict:
    """
        Gets card's data as a json object from API

        Args:
            card_name (str): The name of the MTG card
            modify_name (bool): Replaces space with dashes and removes commas

        Returns:
            dict: an API response as a Python dictionary
    """
    if modify_name:
        card_name = card_name.replace(',', '').replace(' ', '-')

    card_name = card_name.replace('&', 'And')

    response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={card_name}")
    return response.json()


def get_card_info(card_name: str, api_data_func=get_api_data) -> (str, str):
    """
        Gets card's data as a json object from API

        Args:
            card_name (str): The name of an MTG card
            api_data_func (func): The function returning a dictionary containing json response of the API

        Returns:
            (str, str): a tuple containing card's type and image url
    """
    data = api_data_func(card_name)

    if 'object' in data and data['object'] == 'error':
        print(f'Error: {data["details"]}')
        return None, None

    if data['legalities']['brawl'] != 'legal':
        return None, None

    type_priority = ['Instant', 'Sorcery', 'Battle', 'Planeswalker', 'Land', 'Creature', 'Enchantment', 'Artifact']
    card_type_line = data['type_line']
    card_types = card_type_line.split("—")[0].strip().split()
    c_type = sorted(card_types, key=lambda x: type_priority.index(x) if x in type_priority else len(type_priority))[0]

    image_url = data['image_uris']['border_crop'] if 'image_uris' in data else None
    if image_url is None:
        image_url = data['card_faces'][0]['image_uris']['border_crop'] if 'card_faces' in data else None

    return c_type, image_url
