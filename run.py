from app.src import url_scrapper
import requests


def main():
    with open('app/test/pages/AetherhubSingleList.txt', 'w') as f:
        txt = url_scrapper.get_single_deck_data_aetherhub('https://aetherhub.com/Metagame/Historic-Brawl/Deck/etali-primal-conqueror-1036844')
        f.write(txt)


if __name__ == "__main__":
    main()

#  delete from Brawler.Decks where commander_id > 0;
#  delete from Brawler.Commanders where id > 0;
#  delete from Brawler.Cards where id > 0;
