from app.application import app
from behave import given
from app.repository import database
from flask import current_app
from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """enable foreign key constraint for tests"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@given("database is reset")
def step_impl_reset_db(context):
    with app.app_context():
        database.db.init_app(current_app)
        database.db.drop_all()
        database.db.create_all()