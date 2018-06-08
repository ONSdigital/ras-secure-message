from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from secure_message.repository.database import SecureMessage, Events


engine = create_engine('postgresql://postgres:postgres@localhost:6432')
Session = sessionmaker(bind=engine)
session = Session()

try:
    messages_without_sent_at = session.query(SecureMessage).filter(SecureMessage.sent_at == None).all() # noqa
    for message in messages_without_sent_at:
        sent_event = session.query(Events).filter(and_(message.msg_id == Events.msg_id, Events.event == 'Sent')).one_or_none()
        message.sent_at = sent_event.date_time
        session.add(message)

    session.commit()
except SQLAlchemyError:
    session.rollback()
    print("Problem!")
