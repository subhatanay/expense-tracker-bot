from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, Text,Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import uuid
import datetime


Base = declarative_base()

# Utility function to generate UUID
def generate_uuid():
    return str(uuid.uuid4())

# Entity classes (User, Session, Event)
class UserInfo(Base):
    __tablename__ = "user_info"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    fullname = Column(String, unique=False, nullable=False)
    email_id = Column(String, unique=True, nullable=False)
    password = Column(String, unique=False, nullable=False)

class Sessions(Base):
    __tablename__ = "sessions"
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    session_name = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user_info.user_id'), nullable=False)

class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("sessions.session_id"))
    operation = Column(Text, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(Text)
    sub_category = Column(Text)
    date_of_transaction = Column(Date)
    created_date = Column(Date, default=datetime.datetime.utcnow)
    updated_date = Column(Date, default=datetime.datetime.utcnow)

class Events(Base):
    __tablename__ = "events"
    event_id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id'), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transaction.transaction_id'), nullable=False)
    prompt_req = Column(String, nullable=False)
    prompt_res = Column(String, nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow)


