from mysql.connector import Error
from flask import Flask, jsonify, request, copy_current_request_context
from app.src.methods import dbh_init
from threading import BoundedSemaphore
from queue import Queue
import threading

app = Flask(__name__)
sem = BoundedSemaphore(1)
queue = Queue()

PERCENT = 0.6
LOW = 5
HIGH = 30

PORT_NUM = 2138
HOST_NUM = '0.0.0.0'

dbh = dbh_init()

try:
    card_types = dbh.get_card_types()
    color_combinations = dbh.get_colors()
except Error:
    card_types = []
    color_combinations = []


def handle_request(req, func, *args):
    @copy_current_request_context
    def task():
        if len(args) > 0:
            res = func(req, args[0])
        else:
            res = func(req)
        queue.put(res)

    threading.Thread(target=task).start()
    return queue.get()


@app.route('/commanders/popularity', methods=['GET'])
def popular_commanders():
    def popular_commanders_request(req):
        with sem:
            limit = req.args.get('limit', default=10, type=int)
            try:
                commanders = dbh.get_popular_commanders(limit)
            except Error:
                return jsonify([])
            return jsonify(commanders)
    return handle_request(request, popular_commanders_request)


@app.route('/commanders/winrate', methods=['GET'])
def best_winrate_commanders():
    def best_winrate_commanders_request(req):
        with sem:
            limit = req.args.get('limit', default=10, type=int)
            try:
                commanders = dbh.get_best_winrate_commanders(limit)
            except Error:
                return jsonify([])
            return jsonify(commanders)
    return handle_request(request, best_winrate_commanders_request)


@app.route('/cards', methods=['GET'])
def popular_cards():
    def popular_cards_request(req):
        with sem:
            limit = req.args.get('limit', default=10, type=int)
            try:
                cards = dbh.get_popular_cards(limit)
            except Error:
                return jsonify([])
            return jsonify(cards)
    return handle_request(request, popular_cards_request)


@app.route('/commanders/<string:colors>', methods=['GET'])
def commanders_by_color(colors):
    def commanders_by_color_request(_, colors_scope):
        with sem:
            if colors not in dbh.get_colors():
                return jsonify([])
            try:
                commanders = dbh.get_commanders_by_color(colors_scope)
            except Error:
                return jsonify([])
            return jsonify(commanders)
    return handle_request(request, commanders_by_color_request, colors)


@app.route('/commanders/<int:commander_id>', methods=['GET'])
def commander_cards(commander_id):
    def commander_cards_request(_, commander_id_scope):
        with sem:
            commander_cards_dict = {}
            try:
                for card_type in card_types:
                    cards = dbh.get_commander_cards(commander_id=commander_id_scope, card_type=card_type,
                                                    percent=PERCENT, low=LOW, high=HIGH)
                    commander_cards_dict[card_type] = cards
            except Error:
                return jsonify([])
            return jsonify(commander_cards_dict)
    return handle_request(request, commander_cards_request, commander_id)


@app.route('/colors', methods=['GET'])
def return_colors():
    def return_colors_request(_):
        with sem:
            return jsonify(color_combinations)
    return handle_request(request, return_colors_request)


@app.route('/types', methods=['GET'])
def return_types():
    def return_types_request(_):
        with sem:
            return jsonify(card_types)
    return handle_request(request, return_types_request)


if __name__ == '__main__':
    app.run(debug=True, host=HOST_NUM, port=PORT_NUM)
