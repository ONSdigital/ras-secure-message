from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Message(db.Model):

    __tablename__ = "secure_message"
    id = Column(Integer, primary_key=True)
    msg_to = Column("msg_to", String)
    msg_from = Column("msg_from", String)
    body = Column("body", String)

    def __init__(self, msg_to, msg_from, body):
        self.msg_to = msg_to
        self.msg_from = msg_from
        self.body = body
