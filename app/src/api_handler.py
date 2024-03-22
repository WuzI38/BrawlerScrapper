import requests


def get_card_info(card_name: str) -> (str, str):
    response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={card_name}")
    data = response.json()

    if 'object' in data and data['object'] == 'error':
        print(f'Error: {data['details']}')
        return None, None

    type_priority = ['Instant', 'Sorcery', 'Battle', 'Planeswalker', 'Land', 'Creature', 'Enchantment', 'Artifact']
    card_type_line = data['type_line']
    card_types = card_type_line.split("—")[0].strip().split()
    c_type = sorted(card_types, key=lambda x: type_priority.index(x) if x in type_priority else len(type_priority))[0]

    image_url = data['image_uris']['border_crop'] if 'image_uris' in data else None

    return c_type, image_url
