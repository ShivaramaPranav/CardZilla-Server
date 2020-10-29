import sys

sys.path.append(".")
from flask import Flask, request, Response
from models.player import Player
from models.game import Game
from models.deckCard import DeckCard
from models.boardSlot import BoardSlot
from db import db

import random

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://root:password@db:5432/flaskJWT"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
GAMEBOARD = [["x", "y3", "y4", "r5", "r6", "x"],
             ["r4", "b2", "b1", "y4", "r7", "g1"],
             ["r3", "b3", "y5", "b7", "y3", "g2"],
             ["r2", "g1", "y6", "b6", "y2", "g3"],
             ["r1", "g2", "y7", "r1", "y1", "y1"],
             ["b4", "g3", "b1", "r2", "b5", "y2"],
             ["b5", "g4", "b2", "r3", "b4", "r5"],
             ["b6", "g5", "b3", "r4", "g4", "r6"],
             ["b7", "y5", "g7", "g6", "g5", "r7"],
             ["x", "y6", "y7", "g6", "g7", "x"]]
COLORS = ["b", "g", "r", "y"]

db.init_app(app)


@app.route("/")
def home():
    return "Sequence game API Server up and running!"


@app.route("/user/<id>", methods=["GET"])
def getUser(id):
    player = Player.find_by_id(id)
    if player is None:
        return Response("Player for the given userid does not exist", status=200)
    return player.json()


@app.route("/user/create", methods=["GET"])
def createUser():
    player = Player()
    player.save_to_db()
    return player.json()


@app.route("/board/create", methods=["POST"])
def initializeBoard():
    body = request.form
    playerId = int(body.get("playerId"))

    # create game
    game = Game(player1Id=playerId)
    game.save_to_db()

    # create deck
    for i in range(1, 8):
        for j in range(4):
            value = COLORS[j] + str(i)
            card = DeckCard(value, 2, game.id)
            card.save_to_db()
    jack1 = DeckCard("w", 4, game.id)
    jack2 = DeckCard("n", 4, game.id)
    jack1.save_to_db()
    jack2.save_to_db()

    # create board
    for i in range(0, len(GAMEBOARD)):
        for j in range(0, len(GAMEBOARD[i])):
            slot = BoardSlot(GAMEBOARD[i][j], i+1, j+1, game.id)
            slot.save_to_db()

    return game.json()


@app.route("/board/join", methods=["POST"])
def addPlayerToBoard():
    body = request.form
    playerId = int(body.get("playerId"))
    gameId = int(body.get("gameId"))
    game = Game.find_by_id(gameId)
    if game == None or game.player1Id == None:
        return Response("Game does not exist or is corrupted", status=200)

    if game.player2Id != None:
        return Response("Game is full", status=200)

    game.player2Id = playerId
    game.save_to_db()

    return game.json()


@app.route("/board/<id>", methods=["GET"])
def getBoard(id):
    game = Game.find_by_id(id)
    if game is None:
        return Response("Game does not exist", status=200)

    resp = {}
    resp.update({
        "game": game.json()
    })
    bd = []
    boardSlots = BoardSlot.find_by_game(game.id)
    for slot in boardSlots:
        bd.append(slot.json())
    resp.update({
        "board": bd
    })
    return resp


@app.route("/board/<id>/draw", methods=["GET"])
def drawCard(id):
    game = Game.find_by_id(id)
    if game is None:
        return Response("Game does not exist", status=200)
    deckCards = DeckCard.find_by_game(game.id)
    num = random.randint(0, len(deckCards)-1)
    card = deckCards[num]
    card.count -= 1
    if card.count == 0:
        card.delete_from_db()
    else:
        card.save_to_db()
    return card.json()


@app.route("/board", methods=["POST"])
def updateBoard():
    """
        To place or remove a coin
    """
    body = request.form
    row = int(body.get("row"))
    col = int(body.get("column"))
    playerId = int(body.get("playerId"))
    action = body.get("action")
    gameId = int(body.get("gameId"))
    slot = BoardSlot.find_by_row_column(row, col, gameId)
    game = Game.find_by_id(gameId)
    value = GAMEBOARD[row-1][col-1]
    response = {}
    if playerId == game.player1Id:
        game.p1LastPlayed = value
    else:
        game.p2LastPlayed = value

    if action == "place":
        slot.playerId = playerId
    else:
        slot.playerId = None
    slot.save_to_db()


    # vertical
    vertical = []
    for i in range(row - 3, row + 4):
        if 0 < i < 11:
            slot = BoardSlot.find_by_row_column(i, col, gameId)
            vertical.append(slot)
    checkSequence(vertical, playerId, game)

    # horizontal
    horizontal = []
    for i in range(col - 3, col + 4):
        if 0 < i < 7:
            slot = BoardSlot.find_by_row_column(row, i, gameId)
            horizontal.append(slot)
    checkSequence(horizontal, playerId, game)

    # diagnol 1
    diagnol = []
    sumArray = [(-3, -3), (-2, -2), (-1, -1), (0, 0), (1, 1), (2, 2), (3, 3)]
    for i, j in sumArray:
        r, c = row + 1, col + j
        if 0 < r < 11 and 0 < c < 7:
            slot = BoardSlot.find_by_row_column(r, c, gameId)
            diagnol.append(slot)
    checkSequence(diagnol, playerId, game)

    # diagnol 2
    diagnol = []
    sumArray = [(-3, 3), (-2, 2), (-1, 1), (0, 0), (1, -1), (2, -2), (3, -3)]
    for i, j in sumArray:
        r, c = row + 1, col + j
        if 0 < r < 11 and 0 < c < 7:
            slot = BoardSlot.find_by_row_column(r, c, gameId)
            diagnol.append(slot)
    checkSequence(diagnol, playerId, game)

    if game.turn == game.player1Id:
        game.turn = game.player2Id
    else:
        game.turn = game.player1Id

    game.save_to_db()
    response.update({
        "game": game.json()
    })

    return response


def checkSequence(arr, playerId, game):
    length = len(arr)
    for i in range(4):
        sequence = []
        for j in range(i, i + 4):
            if j < length:
                print(j)
                slot = arr[j]
                if slot.playerId == playerId or slot.value == 'x':
                    num = (slot.row - 1 * 6) + slot.column
                    sequence.append(num)
                else:
                    break
            else:
                break
        if len(sequence) == 4:
            seq = str(sequence)[1:-1]
            if playerId == game.player1Id:
                if game.p1s1 in (None, ""):
                    game.p1s1 = seq
                elif not isMoreThan1Repeated(game.p1s1, seq):
                    game.p1s2 = seq
                    game.winnerId = playerId
            else:
                if game.p2s1 in (None, ""):
                    game.p2s1 = seq
                elif not isMoreThan1Repeated(game.p2s1, seq):
                    game.p2s2 = seq
                    game.winnerId = playerId
            break


def isMoreThan1Repeated(s1, s2):
    count = 0
    for ch in s2:
        if ch in s1:
            if count > 1:
                return True
            else:
                count+=1
    return False


def getSequenceJson(slots):
    json = []
    for slot in slots:
        json.append(slot.json())
    return json


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":
    db.init_app(app)
    app.run(host="0.0.0.0", port=5000)
