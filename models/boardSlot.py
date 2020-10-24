import sys

sys.path.append("..")

from db import db


class BoardSlot(db.Model):
    __tablename__ = 'boardslot'

    id = db.Column(db.Integer, primary_key=True)
    row = db.Column(db.Integer, nullable=False)
    column = db.Column(db.Integer, nullable=False)
    value = db.Column(db.String(80), nullable=False)
    playerId = db.Column(db.Integer, nullable=True)
    gameId = db.Column(db.Integer, db.ForeignKey('game.id'))  # -
    game = db.relationship("Game", backref=db.backref("game", uselist=False))

    def __init__(self, value, row, column, gameId, playerId=None):
        self.value = value
        self.row = row
        self.column = column
        self.gameId = gameId
        self.playerId = playerId

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_game(cls, id):
        return cls.query.filter_by(gameId=id).all()

    @classmethod
    def find_by_row_column(cls, row, column, gameId):
        return cls.query.filter_by(row=row).filter_by(column=column).filter_by(gameId=gameId).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {
            "value": self.value,
            "row": self.row,
            "column": self.column,
            "playerId": self.playerId
        }
