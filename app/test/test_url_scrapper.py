from ..src.url_scrapper import (create_aetherhub_deck_list, create_mtgdecks_deck_list,
                                create_aetherhub_single_deck_dict, create_mtgdecks_single_deck_dict)
import os


def mock_page_data(path: str) -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, path), 'r') as f:
        return f.read()


def test_create_aetherhub_deck_list_correct():
    txt = mock_page_data('pages/AetherhubDecks.txt')
    lst = create_aetherhub_deck_list(txt)
    assert isinstance(lst, list)
    assert len(lst) > 0


def test_create_aetherhub_deck_list_error():
    txt = mock_page_data('pages/AetherhubErr.txt')
    lst = create_aetherhub_deck_list(txt)
    assert isinstance(lst, list)
    assert len(lst) == 0


def test_create_mtgdecks_deck_list_correct():
    txt = mock_page_data('pages/MtgdecksDecks.txt')
    lst = create_mtgdecks_deck_list(txt)
    assert isinstance(lst, list)
    assert len(lst) > 0


def test_create_mtgdecks_deck_list_error():
    txt = mock_page_data('pages/MtgdecksErr.txt')
    lst = create_mtgdecks_deck_list(txt)
    assert isinstance(lst, list)
    assert len(lst) == 0


def test_create_aetherhub_single_deck_dict_correct():
    txt = mock_page_data('pages/AetherhubSingleList.txt')
    lst = create_aetherhub_single_deck_dict(txt)
    assert isinstance(lst, dict)
    assert len(lst) > 0


def test_create_aetherhub_single_deck_dict_error():
    txt = mock_page_data('pages/AetherhubErr.txt')
    lst = create_aetherhub_single_deck_dict(txt)
    assert isinstance(lst, dict)
    assert len(lst) == 0


def test_create_mtgdecks_single_deck_dict_correct():
    txt = mock_page_data('pages/MtgdecksSingleList.txt')
    lst = create_mtgdecks_single_deck_dict(txt)
    assert isinstance(lst, dict)
    assert len(lst) > 0


def test_create_mtgdecks_single_deck_dict_error():
    txt = mock_page_data('pages/MtgdecksErr.txt')
    lst = create_mtgdecks_single_deck_dict(txt)
    print(lst)
    assert isinstance(lst, dict)
    assert len(lst) == 0
