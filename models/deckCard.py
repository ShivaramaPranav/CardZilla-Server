import sys
sys.path.append("..")

from db import db


class DeckCard(db.Model):
    __tablename__ = 'deckcard'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(80), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    gameId = db.Column(db.Integer, db.ForeignKey('game.id'))

    def __init__(self, value, count, gameId):
        self.value = value
        self.count = count
        self.gameId = gameId

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_game(cls, id):
        return cls.query.filter_by(gameId=id).filter(DeckCard.count>0).all()

    @classmethod
    def find_by_name(cls, value):
        return cls.query.filter_by(value=value).first()

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
            "id": self.id,
            "value": self.value,
            "count": self.count
        }