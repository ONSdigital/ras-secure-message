from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import logging


logger = logging.getLogger(__name__)

db = SQLAlchemy()


class Message(db.Model):
    """Secure messaging datasbase model"""
    logger.debug("Hit database message")

    __tablename__ = "secure_message"
    id = db.Column(Integer, primary_key=True)
    msg_to = db.Column("msg_to", String)
    msg_from = db.Column("msg_from", String)
    body = db.Column("body", String)

    def __init__(self, msg_to=None, msg_from=None, body=None):
        self.msg_to = msg_to
        self.msg_from = msg_from
        self.body = body

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        data = {
           'id': self.id,
           'msg_to': self.msg_to,
           'msg_from': self.msg_from,
           'body': self.body
        }
        return data
