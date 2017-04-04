from app.data_model import database
from sqlalchemy import create_engine
from flask import current_app
from app.application import app
from app import application


def before_scenario(context, scenario):
    context.app = application.app.test_client()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
    engine = create_engine('sqlite:////tmp/messages.db', echo=True)
    with app.app_context():
        database.db.init_app(current_app)
        database.db.drop_all()
        database.db.create_all()
        db = database.db

    with engine.connect() as con:
        for i in range(3):
            query = 'INSERT INTO secure_message VALUES ({},"test", "test", "test","test","",0,0,\
            "2017-02-03 00:00:00", "2017-02-03 00:00:00")'.format(i)
            con.execute(query)
