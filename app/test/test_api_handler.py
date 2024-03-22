from json import load
from ..src.api_handler import get_card_info
import os


def mock_api_data(path: str) -> dict:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, path)) as f:
        return load(f)


def test_get_card_info_error():
    card_type, image_url = get_card_info('api/ErrorResponse.json', api_data_func=mock_api_data)
    assert card_type is None
    assert image_url is None


def test_get_card_info_correct():
    card_type, url = get_card_info('api/CorrectResponse.json', api_data_func=mock_api_data)
    assert card_type == 'Creature'
    assert url == 'https://cards.scryfall.io/border_crop/front/7/1/71f2b7ac-8742-468d-b6a3-87881cb522ff.jpg?1591227501'
