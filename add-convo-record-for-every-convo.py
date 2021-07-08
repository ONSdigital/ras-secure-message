import sys
from sqlite3 import DatabaseError

from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker

from config import Config
from secure_message.repository.database import Conversation, SecureMessage

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
db = Session()

try:
    subquery = db.query(Conversation.id)
    distinct_ids = db.query(SecureMessage.thread_id).filter(~SecureMessage.thread_id.in_(subquery)).distinct()
    for thread_id in distinct_ids:
        db.execute(insert(Conversation).values({"id": thread_id, "is_closed": "False"}))
        print("Added thread_id: {}".format(thread_id[0]))
    db.commit()
except DatabaseError:
    db.rollback()
    print(DatabaseError)
    sys.exit("Exiting")
