from flask import Flask, jsonify, request
from app.src.methods import dbh_init

app = Flask(__name__)

PERCENT = 0.6
LOW = 5
HIGH = 30

PORT_NUM = 2138
HOST_NUM = '0.0.0.0'

dbh = dbh_init()
card_types = dbh.get_card_types()
color_combinations = dbh.get_colors()


@app.route('/api/commanders/popularity', methods=['GET'])
def popular_commanders():
    # http://127.0.0.1:2138/api/commanders/popularity?limit=3
    limit = request.args.get('limit', default=10, type=int)
    commanders = dbh.get_popular_commanders(limit)
    return jsonify(commanders)


@app.route('/api/commanders/winrate', methods=['GET'])
def best_winrate_commanders():
    # http://127.0.0.1:2138/api/commanders/winrate?limit=3
    limit = request.args.get('limit', default=10, type=int)
    commanders = dbh.get_best_winrate_commanders(limit)
    return jsonify(commanders)


@app.route('/api/cards/popularity', methods=['GET'])
def popular_cards():
    # http://127.0.0.1:2138/api/cards/popularity?limit=3
    limit = request.args.get('limit', default=10, type=int)
    cards = dbh.get_popular_cards(limit)
    return jsonify(cards)


@app.route('/api/commanders/<string:colors>', methods=['GET'])
def commanders_by_color(colors):
    # http://127.0.0.1:2138/api/commanders/wb
    if colors not in dbh.get_colors():
        return jsonify([])
    commanders = dbh.get_commanders_by_color(colors)
    return jsonify(commanders)


@app.route('/api/commanders/<int:commander_id>', methods=['GET'])
def commander_cards(commander_id):
    # http://127.0.0.1:2138/api/commanders/70
    commander_cards_dict = {}
    for card_type in card_types:
        cards = dbh.get_commander_cards(commander_id=commander_id, card_type=card_type,
                                        percent=PERCENT, low=LOW, high=HIGH)
        commander_cards_dict[card_type] = cards
    return jsonify(commander_cards_dict)


@app.route('/api/colors', methods=['GET'])
def return_colors():
    # http://127.0.0.1:2138/api/colors
    return jsonify(color_combinations)


@app.route('/api/types', methods=['GET'])
def return_types():
    # http://127.0.0.1:2138/api/types
    return jsonify(card_types)


if __name__ == '__main__':
    app.run(debug=True, host=HOST_NUM, port=PORT_NUM)
