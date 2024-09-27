from services import UserService, SessionService, EventService, DbConnection, TransactionService
from datetime import datetime, timedelta
from db_entity import UserInfo, Sessions, Events, Transaction
from email_sender import send_email
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging


session_db = None
user_service = None
session_service = None
event_service = None
transaction_service = None

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Define the format
)
# Create a logger object
logger = logging.getLogger(__name__)


def start_db_session():
    session_db = DbConnection().get_db_session()
    user_service = UserService(session_db)
    session_service = SessionService(session_db)
    event_service = EventService(session_db)
    transaction_service = TransactionService(session_db)


def cleanup_db_session(exception=None):
    
    if session_db:
        if exception:
            session_db.rollback()  # Rollback on any exception
        else:
            db.commit()  # Commit if no exception
        session_db.close() 

def generate_consolidated_report(period: str):
    exception = False
    try:
        start_db_session()
        # Determine the start date based on the period
        today = datetime.now()
        if period == 'week':
            start_date = today - timedelta(weeks=1)
        elif period == 'month':
            start_date = today.replace(day=1)
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
        else:
            logger.error("Invalid period specified. Choose from 'week', 'month', 'year'.")
            return
        
        # Fetch all users
        users = session_db.query(UserInfo).all()

        for user in users:
            user_email = user.email_id
            if not user_email:
                logger.info(f"User {user.user_id} does not have an email. Skipping.")
                continue
            
            # Initialize totals
            total_income = 0
            total_expense = 0
            
            # Initialize report HTML
            report_html = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        color: #333333;
                    }}
                    .report-container {{
                        width: 100%;
                        max-width: 800px;
                        margin: auto;
                    }}
                    .report-header {{
                        text-align: center;
                        padding: 20px 0;
                    }}
                    .report-title {{
                        font-size: 24px;
                        margin-bottom: 10px;
                    }}
                    .report-period {{
                        font-size: 18px;
                        color: #555555;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 30px;
                    }}
                    th, td {{
                        border: 1px solid #dddddd;
                        text-align: left;
                        padding: 12px;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                    tr:nth-child(even) {{
                        background-color: #fafafa;
                    }}
                    .footer {{
                        text-align: center;
                        font-size: 14px;
                        color: #777777;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="report-container">
                    <div class="report-header">
                        <div class="report-title">{period.capitalize()} Transaction Report</div>
                        <div class="report-period">for {start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}</div>
                    </div>
            """

            sessions = session_db.query(Sessions).filter(Sessions.user_id == user.user_id).all()
            for user_session in sessions:
                # Fetch transactions for this session within the date range
                transactions = session_db.query(Transaction).filter(
                    Transaction.session_id == user_session.session_id,
                    Transaction.date_of_transaction >= start_date.date(),
                    Transaction.date_of_transaction <= today.date()
                ).all()
                
                if not transactions:
                    continue  # No transactions for this session in the period
                
                # Calculate totals for this session
                session_income = sum(t.amount for t in transactions if t.operation.lower() == 'income')
                session_expense = sum(t.amount for t in transactions if t.operation.lower() == 'expense')
                
                total_income += session_income
                total_expense += session_expense
                
                # Add session-specific report
                report_html += f"""
                    <h3>Session: {user_session.session_name}</h3>
                    <table>
                        <tr>
                            <th>Date of Transaction</th>
                            <th>Category</th>
                            <th>Subcategory</th>
                            <th>Amount</th>
                        </tr>
                """
                
                for txn in transactions:
                    date_str = txn.date_of_transaction.strftime('%Y-%m-%d') if isinstance(txn.date_of_transaction, datetime) else str(txn.date_of_transaction)
                    category = txn.category or "N/A"
                    subcategory = txn.sub_category or "N/A"
                    amount = f"{txn.amount}"
                    
                    report_html += f"""
                        <tr>
                            <td>{date_str}</td>
                            <td>{category}</td>
                            <td>{subcategory}</td>
                            <td>{amount}</td>
                        </tr>
                    """
                
                report_html += "</table>"
            
                # Add total income and expense to the report
                report_html += f"""
                    <h3>Total Income: {total_income}</h3>
                    <h3>Total Expense: {total_expense}</h3>
                    <div class="footer">
                        Thank you for using our Expense Tracker Service!
                    </div>
                </div>
                </body>
                </html>
                """

                try: 
                    send_email(
                        receiver_email=user_email, 
                        subject=f"{period.capitalize()} Transaction Report",
                        message_body=report_html)
                except Exception as ex:
                    logger.error(f"Failed to send email to {user_email}: {ex}")
        logger.info(f"Consolidated {period} reports generated and sent to all users.")
    
    except Exception as e:
        logger.error(f"Error generating consolidated report: {e}")
        exception = True
    finally:
        cleanup_db_session(exception)


def weekly_report_task():
    generate_consolidated_report('week')

def monthly_report_task():
    generate_consolidated_report('month')

def yearly_report_task():
    generate_consolidated_report('year')


def initiate_scheduled_task():
    try: 
        scheduler = BackgroundScheduler()
        # Schedule weekly task: Every Monday at 9:00 AM
        weekly_trigger = CronTrigger(day_of_week='mon', hour=9, minute=0)
        scheduler.add_job(weekly_report_task, trigger=weekly_trigger, id='weekly_task')

        # Schedule monthly task: 1st day of every month at 10:00 AM
        monthly_trigger = CronTrigger(day=1, hour=10, minute=0)
        scheduler.add_job(monthly_report_task, trigger=monthly_trigger, id='monthly_task')

        # Schedule yearly task: January 1st every year at 11:00 AM
        yearly_trigger = CronTrigger(month=1, day=1, hour=11, minute=0)
        scheduler.add_job(yearly_report_task, trigger=yearly_trigger, id='yearly_task')

        # Start the scheduler
        scheduler.start()
        logger.info("Report Scheduler started. ")
    except Exception as ex:
        logger.error(f'Unable to start Report Scheduler : Reasan {ex}')
