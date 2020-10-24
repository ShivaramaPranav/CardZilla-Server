import sys

sys.path.append("..")

from db import db


class Game(db.Model):
    __tablename__ = 'game'

    id = db.Column(db.Integer, primary_key=True)
    player1Id = db.Column(db.Integer, nullable=False)
    player2Id = db.Column(db.Integer, nullable=True)
    turn = db.Column(db.Integer)
    winnerId = db.Column(db.Integer)
    p1s1 = db.Column(db.String(100))
    p1s2 = db.Column(db.String(100))
    p2s1 = db.Column(db.String(100))
    p2s2 = db.Column(db.String(100))
    p1LastPlayed = db.Column(db.String(10))
    p2LastPlayed = db.Column(db.String(10))

    def __init__(self, player1Id, player2Id=None):
        self.player1Id = player1Id
        self.player2Id = player2Id
        self.turn = player1Id

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

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
            "player1Id": self.player1Id,
            "player2Id": self.player2Id,
            "turn": self.turn,
            "winnerId": self.winnerId,
            "p1s1": self.p1s1,
            "p1s2": self.p1s2,
            "p2s1": self.p2s1,
            "p2s2": self.p2s2,
            "p1LastPlayed": self.p1LastPlayed,
            "p2LastPlayed": self.p2LastPlayed
        }
