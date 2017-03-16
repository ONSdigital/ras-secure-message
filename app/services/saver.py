from app.data_model.database import db
from app.data_model import database
from app.domain_model import domain

class Saver():


    def saveMessage(self, message):
        db_message = self.convertToDataModel(message)
        db.session.add(db_message)
        db.session.commit()

    def convertToDataModel(self, domainMessage):
        return database.Message(domainMessage.msg_to, domainMessage.msg_from, domainMessage.body)

