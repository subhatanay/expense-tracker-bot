from sqlalchemy.orm import Session
from datetime import date, datetime
from sqlalchemy import desc
from db_entity import UserInfo, Sessions, Events, Transaction
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()


class DbConnection:
    def __init__(self):
        db_host = os.getenv('DB_HOST', 'localhost')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASS', '')
        db_port = os.getenv('DB_PORT', '5432')

        # Database URL for PostgreSQL
        DATABASE_URL = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/expense_tracker'

        # Create engine with connection pool settings (default QueuePool)
        self.engine = create_engine(
            DATABASE_URL,
            pool_size=10,          # Number of connections to keep open
            max_overflow=5,         # Number of extra connections that can be created if the pool is full
            pool_timeout=30,        # Maximum wait time for a connection from the pool
            pool_recycle=1800       # Recycle connections after 30 minutes to prevent stale connections
        )

        # Create session factory bound to this engine
        self.SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

    def get_db_session(self):
        """Return a new session from the pool."""
        return self.SessionLocal

# Service for UserInfo entity
class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_emailid(self, email_id: str):
        return self.db.query(UserInfo).filter(UserInfo.email_id == email_id).first()

    def add_user(self, email_id: str, name: str, password: str):
        user = self.get_user_by_emailid(email_id)
        if user:
            raise Exception(f'User with email id {email_id} already exists')
        
        new_user = UserInfo(email_id=email_id, fullname = name, password=self.hash_password(password))
        self.db.add(new_user)
        self.db.flush()
        return new_user

    def get_user(self, user_id: str):
        return self.db.query(UserInfo).filter(UserInfo.user_id == user_id).first()

    def verify_user(self, email_id: str, password: str):
        user = self.db.query(UserInfo).filter(UserInfo.email_id == email_id).first()

        if user is None:
            return None, False

        if self.check_password(password, user.password):
            return user, True

        return user, False

    def delete_user(self, user_id: str):
        user = self.get_user(user_id)
        if user:
            self.db.delete(user)
            self.db.flush()
        return user

    def hash_password(self, password: str) -> str:
        # Convert the password to bytes before hashing
        password_bytes = password.encode('utf-8')

        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)

        # Convert the hashed password to a string before returning
        return hashed_password.decode('utf-8')

    def check_password(self, password: str, hashed_password: str) -> bool:
        password_bytes = password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')

        # Verify if the provided password matches the hashed password
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)

# Service for Sessions entity
class SessionService:
    def __init__(self, db: Session):
        self.db = db

    def add_session(self, session_name: str, user_id: str):
        new_session = Sessions(session_name=session_name, user_id=user_id)
        self.db.add(new_session)
        self.db.flush()
        return new_session

    def get_session(self, session_id: str):
        return self.db.query(Sessions).filter(Sessions.session_id == session_id).first()

    def get_sessions_by_user(self, user_id: str):
        return self.db.query(Sessions).filter(Sessions.user_id == user_id).all()

    def delete_session(self, session_id: str):
        session = self.get_session(session_id)
        if session:
            self.db.delete(session)
        return session

# Service for Events entity
class EventService:
    def __init__(self, db: Session):
        self.db = db

    def add_event(self, session_id: str, prompt_req: str, prompt_res: str, transaction_id: str):
        new_event = Events(
            session_id=session_id,
            prompt_req=prompt_req,
            prompt_res=prompt_res,
            transaction_id=transaction_id,
            created_date=date.today(),
            updated_date=date.today()
        )
        self.db.add(new_event)
        self.db.flush()
        return new_event

    def get_event(self, event_id: str):
        return self.db.query(Events).filter(Events.event_id == event_id).first()

    def get_events_by_session(self, session_id: str):
        return self.db.query(Events).filter(Events.session_id == session_id).order_by((Events.created_date)).all()

    def delete_event(self, event_id: str):
        event = self.get_event(event_id)
        if event:
            self.db.flush()
        return event

class TransactionService:
    def __init__(self, db):
        self.db_session = db

    def add_transaction(self, session_id, operation, amount, category, sub_category, date_of_transaction):
        new_transaction = Transaction(
            session_id=session_id,
            operation=operation,
            amount=amount,
            category=category,
            sub_category=sub_category,
            date_of_transaction=date_of_transaction
        )
        self.db_session.add(new_transaction)
        self.db_session.flush()
        return new_transaction

    def get_transaction(self, transaction_id):
        return self.db_session.query(Transaction).filter_by(transaction_id=transaction_id).first()

    def get_total(self, session_id: str, action: str, period: str, date: datetime):
        query = ""
        params = {}

        if period == 'day':
            query = """
                SELECT SUM(amount) as total
                FROM transaction
                WHERE operation = :action AND session_id= :session_id
                AND date_of_transaction = :date
            """
            params = {'action': action, 'date': date.date(), 'session_id': session_id}  # Strip time from datetime for exact day comparison

        elif period == 'month':
            query = """
                SELECT SUM(amount) as total
                FROM transaction
                WHERE operation = :action
                AND EXTRACT(MONTH FROM date_of_transaction) = :month AND session_id= :session_id
                AND EXTRACT(YEAR FROM date_of_transaction) = :year
            """
            params = {'action': action, 'month': date.month, 'year': date.year, 'session_id': session_id}

        elif period == 'year':
            query = """
                SELECT SUM(amount) as total
                FROM transaction
                WHERE operation = :action AND session_id= :session_id
                AND EXTRACT(YEAR FROM date_of_transaction) = :year
            """
            params = {'action': action, 'year': date.year, 'session_id': session_id}
        else:
            raise ValueError("Invalid period. Choose from 'day', 'month', or 'year'.")

        result = self.db_session.execute(text(query), params)
        total = result.scalar()  # Returns the first column of the first row
        return total if total is not None else 0

    def get_transaction_report(self, session_id: str, action: str, period: str, date: datetime):
        query = ""
        params = {}

        if period == 'day':
            query = """
                SELECT date_of_transaction, category, sub_category, amount
                FROM transaction
                WHERE operation = :action AND session_id= :session_id
                AND date_of_transaction = :date
                ORDER BY date_of_transaction ASC
            """
            params = {'action': action, 'date': date.date(), 'session_id': session_id}

        elif period == 'month':
            query = """
                SELECT date_of_transaction, category, sub_category, amount
                FROM transaction
                WHERE operation = :action AND session_id= :session_id
                AND EXTRACT(MONTH FROM date_of_transaction) = :month
                AND EXTRACT(YEAR FROM date_of_transaction) = :year
                ORDER BY date_of_transaction ASC
            """
            params = {'action': action, 'month': date.month, 'year': date.year, 'session_id': session_id}

        elif period == 'year':
            query = """
                SELECT date_of_transaction, category, sub_category, amount
                FROM transaction
                WHERE operation = :action
                AND EXTRACT(YEAR FROM date_of_transaction) = :year
                ORDER BY date_of_transaction ASC
            """
            params = {'action': action, 'year': date.year}

        else:
            raise ValueError("Invalid period. Choose from 'day', 'month', or 'year'.")

        result = self.db_session.execute(text(query), params)
        transactions = result.fetchall()

        transaction_list = []
        for txn in transactions:
            transaction = {
                'date_of_transaction': txn[0],
                'category': txn[1],
                'sub_category': txn[2],
                'amount': float(txn[3])
            }
            transaction_list.append(transaction)

        return transaction_list
        


    def delete_transaction(self, transaction_id):
        transaction = self.db_session.query(Transaction).filter_by(transaction_id=transaction_id).first()
        if transaction:
            self.db_session.delete(transaction)