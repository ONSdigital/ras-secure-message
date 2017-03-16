from app.data_model.database import db
from app.data_model import database


class Saver:

    def save_message(self, message):
        db_message = self.convert_to_datamodel(message)
        db.session.add(db_message)
        db.session.commit()

    @staticmethod
    def convert_to_datamodel(domain_message):
        return database.Message(domain_message.msg_to, domain_message.msg_from, domain_message.body)
