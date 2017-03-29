from app.data_model.database import db
from app.data_model import database


class Saver:
    """Created when saving a message"""

    @staticmethod
    def save_message(domain_message):
        """save message to database"""
        db_message = database.DbMessage()
        db_message.set_from_domain_model(domain_message)
        db.session.add(db_message)
        db.session.commit()

    @staticmethod
    def convert_to_datamodel(domain_message):
        return database.DbMessage(domain_message.msg_to, domain_message.msg_from, domain_message.subject,
                                  domain_message.body, domain_message.thread, domain_message.archived,
                                  domain_message.marked_as_read, domain_message.create_date, domain_message.read_date,
                                  domain_message.msg_id)
