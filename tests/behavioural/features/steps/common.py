from app.application import app
from behave import given
from app.repository import database
from flask import current_app


@given("database is reset")
def step_impl_reset_db(context):
    with app.app_context():
        database.db.init_app(current_app)
        database.db.drop_all()
        database.db.create_all()