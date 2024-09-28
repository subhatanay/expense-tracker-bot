import google.generativeai as genai
from services import UserService, SessionService, DbConnection, TransactionService
from datetime import datetime
import logging
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Define the format
)
# Create a logger object
logger = logging.getLogger(__name__)

class ExpenseChat:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_KEY', '')
        self.chat_session = {}
        self.ask_on_expense_prompt_template = """
I'll provide you with a CSV file containing my expenses and income. You'll be asked questions about this data. Please answer only questions related to the provided information in a clear, text-based format. Avoid answering unrelated questions or providing image responses.
In response, for amount total use Indian Rupee format. 
In response, when you get some csv or report response , list of trasaction with date , return as plain html response with a simple table format
else plain text is enough
In response, when you wanted to highlight something, try to use html tags.
Here are some examples of questions you might be asked:

What is my total spending across all sessions?
How much have I spent on groceries, doctor's visits, and medicine in the past three months?
The CSV file will have the following columns:

session_name: The name of the expense session (e.g., daily expenses, stocks, travel planning)
type: Whether it's an expense or income
date_of_transaction: The date of the transaction
category: The category of the expense or income
amount: The amount spent or earned

Here is the csv data of my transaction statements : 

<CSV_DATA>
"""
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        genai.configure(api_key=self.api_key)

    def format_csv(self, transaction_statement_csv, session, expenses, incomes):
        for expense in expenses:
            transaction_statement_csv += f'{session.session_name}, expense, {expense["date_of_transaction"].strftime("%Y-%m-%d")}, {expense["category"]}, {expense["amount"]}\n'

        for income in incomes:
            transaction_statement_csv += f'{session.session_name}, income, {income["date_of_transaction"].strftime("%Y-%m-%d")}, {income["category"]}, {income["amount"]}\n'

        return transaction_statement_csv

    def get_transaction_statement_for_user(self, user_id):
        session_db = DbConnection().get_db_session()
        transaction_statement_csv = "session_name, type, date_of_transaction, category, amount\n"
        try:
            session_service = SessionService(session_db)
            transaction_service = TransactionService(session_db)

            sessions = session_service.get_sessions_by_user(user_id)

            for session in sessions:
                expenses = transaction_service.get_transaction_report(session.session_id, 'expense', 'all', None)
                incomes = transaction_service.get_transaction_report(session.session_id, 'income', 'all', None)

                transaction_statement_csv = self.format_csv(transaction_statement_csv, session, expenses, incomes)
        except Exception as ex:
            logger.error(f'Error while fetching transaction statement - {ex}')
            return None
        finally:
            if session_db:
                session_db.close()

        return transaction_statement_csv

    def initiate_chat_session_for_user(self, user_id, initial_prompt):
        try:
            chat = self.model.start_chat(
                history=[
                    {"role": "user", "parts": "Hello"},
                    {"role": "model", "parts": initial_prompt}
                ]
            )
            return chat
        except Exception as ex:
            logger.info(f'Unable to initate chat with gemini. Error : {ex}')
            raise Exception(f'Unable to initate chat with gemini. Error : {ex.message}')

    def init_ask_me_on_expense_chat(self, user_id):
        transaction_statement_csv = self.get_transaction_statement_for_user(user_id) 
        if transaction_statement_csv is None or transaction_statement_csv.count('\n') == 1:
            raise Exception("No transaction data available. Create some expenses and comeback here.")

        final_prompt = self.ask_on_expense_prompt_template.replace('<CSV_DATA>', transaction_statement_csv)

        chat = self.initiate_chat_session_for_user(user_id, final_prompt)
        if chat:
            self.chat_session[user_id] = chat
            return True
        
        return False

    def ask_follow_up_qs(self, user_id, follow_question):
        if user_id in self.chat_session:
            response = self.chat_session[user_id].send_message(follow_question)
            return response.text

        raise Exception("User hasn't started any chat session.")

    def close_chat(self, user_id):
        if user_id in self.chat_session:
            # self.chat_session[user_id].close()
            del self.chat_session[user_id]
        else:
            raise Exception("User hasn't started any chat session.")



            
