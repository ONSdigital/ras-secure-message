from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from secure_message.repository.database import SecureMessage, Events
from config import Config # NOQA

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

try:
    messages_without_sent_at = session.query(SecureMessage).filter(SecureMessage.sent_at == None).all() # noqa
    for message in messages_without_sent_at:
        sent_event = session.query(Events).filter(and_(message.msg_id == Events.msg_id, Events.event == 'Sent')).one_or_none()
        if sent_event is not None:
            message.sent_at = sent_event.date_time
            session.add(message)
    session.commit()
except Exception as e:
    session.rollback()
    print(e)


try:
    messages_without_read_at = session.query(SecureMessage).filter(SecureMessage.read_at == None).all() # noqa
    for message in messages_without_read_at:
        read_event = session.query(Events).filter(and_(message.msg_id == Events.msg_id, Events.event == 'Read')).one_or_none()
        if read_event is not None:
            message.read_at = read_event.date_time
            session.add(message)
    session.commit()
except Exception as e:
    session.rollback()
    print(e)
