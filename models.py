# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Conversation(Base):
    __tablename__ = 'conversation'
    __table_args__ = {'schema': 'securemessage'}

    id = Column(String(60), primary_key=True, index=True)
    is_closed = Column(Boolean)
    test2 = Column(Boolean)
    closed_by = Column(String)
    closed_by_uuid = Column(String(60))
    closed_at = Column(DateTime)
    category = Column(String(60), server_default=text("'SURVEY'::character varying"))


class SecureMessage(Base):
    __tablename__ = 'secure_message'
    __table_args__ = (
        Index('idx_ru_survey_cc', 'business_id', 'survey_id', 'case_id', 'exercise_id'),
        # Index('ix_securemessage_secure_message_msg_id','msg_id'),
        #a Index('ix_securemessage_secure_message_thread_id','thread_id'),
        # UniqueConstraint('msg_id'),
        {'schema': 'securemessage'}
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('securemessage.secure_message_id_seq'::regclass)"))
    msg_id = Column(String(60), index = True, unique = True)
    subject = Column(String(101))
    body = Column(String(50001))
    thread_id = Column(ForeignKey('securemessage.conversation.id'), index=True)
    case_id = Column(String(61))
    business_id = Column(String(61))
    exercise_id = Column(String(61))
    survey_id = Column(String(61))
    from_internal = Column(Boolean)
    sent_at = Column(DateTime)
    read_at = Column(DateTime)

    thread = relationship('Conversation')


class Event(Base):
    __tablename__ = 'events'
    __table_args__ = (
        Index('idx_msg_id_event', 'msg_id', 'event'),
        {'schema': 'securemessage'}
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('securemessage.events_id_seq'::regclass)"))
    event = Column(String(21))
    msg_id = Column(ForeignKey('securemessage.secure_message.msg_id'), index=True)
    date_time = Column(DateTime)

    msg = relationship('SecureMessage')


class Status(Base):
    __tablename__ = 'status'
    __table_args__ = (
        Index('idx_msg_id_label', 'msg_id', 'label'),
        {'schema': 'securemessage'}
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('securemessage.status_id_seq'::regclass)"))
    label = Column(String(51))
    msg_id = Column(ForeignKey('securemessage.secure_message.msg_id'))
    actor = Column(String(101))

    msg = relationship('SecureMessage')
