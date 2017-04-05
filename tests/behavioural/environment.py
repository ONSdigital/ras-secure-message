import uuid

from flask import current_app
from sqlalchemy import create_engine

from app import application
from app.application import app
from app.repository import database


def before_scenario(context):
    context.app = application.app.test_client()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
    engine = create_engine('sqlite:////tmp/messages.db', echo=True)
    with app.app_context():
        database.db.init_app(current_app)
        database.db.drop_all()
        database.db.create_all()
        database.db

    with engine.connect() as con:
        for i in range(3):
            msg_id = str(uuid.uuid4())
            query = 'INSERT INTO secure_message VALUES ({0}, "{1}", "test", "test", "test","test","",\
                             "2017-02-03 00:00:00", "2017-02-03 00:00:00", "ACollectionCase",\
                             "AReportingUnit", "ACollectionInstrument")'.format(i, msg_id)

            con.execute(query)
