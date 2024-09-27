from flask import Flask, g, jsonify, request, abort
from sqlalchemy.orm import sessionmaker
from services import UserService, SessionService, EventService, DbConnection, TransactionService  # Import your service classes
from expense_model import ExpenseTrackerModel
from flask_cors import CORS,cross_origin
from command_parser import extract_command_info
from email_sender import send_email
from email_template import format_transaction_report_html
from report_task import initiate_scheduled_task
from jwt_token_filter import token_required
from jwt_utils import generate_token
import logging

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize services
db_conn = DbConnection()
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Define the format
)
# Create a logger object
logger = logging.getLogger(__name__)

@app.before_request
def create_db_session():
    g.db = db_conn.get_db_session()
    g.excep = None

@app.teardown_request
def cleanup_db_session(exception=None):
    excep = g.get('excep')
    db: Session = g.get('db')
    if db:
        if excep:
            db.rollback()  # Rollback on any exception
        else:
            db.commit()  # Commit if no exception
        db.close() 


@app.route('/users', methods= ['POST'])
def create_user():
    try: 
        if not request.json:
            return jsonify({
                'error_code': 400,
                'description': "Missing request body",
            }), 400

        name = request.json['fullname']
        email_id = request.json['email']
        password = request.json['pass']

        user_service = UserService(g.db)
        user = user_service.add_user(name = name, email_id = email_id, password = password)
        logging.info(f'Created user: {user.user_id}')

        return jsonify({
            'user_id': user.user_id,
        }), 201
    except Exception as ex:
        g.excep = ex
        logging.info(f'Error in create_user {ex} ')
        return jsonify({
            'error_code': 500,
            'description': f'Internal server error - {ex}',
        }), 500

    

@app.route('/users/login', methods= ['POST'])
def login_user():
    try: 
        if not request.json:
            return jsonify({
                'error_code': 400,
                'description': "Missing request body... ",
            }), 400

        email_id = request.json['email']
        password = request.json['pass']

        user_service = UserService(g.db)
        user, isValid = user_service.verify_user(email_id = email_id, password = password)
        if isValid == True:
            return jsonify({
                'user_id': str(user.user_id),
                'full_name': user.fullname,
                'token': generate_token({ 'user_id': str(user.user_id) })
            }), 200
        
        return jsonify({
            'error_code': 401,
            'description': "Invalid token or unauthenticated entity",
        }), 401

    except Exception as ex:
        g.excep = ex
        logging.error(f'Error in login_user {ex} ')
        return jsonify({
            'error_code': 500,
            'description': "Internal server error ",
        }), 500
        


# POST /users/<userId>/sessions -> Create a new session for a user
@app.route('/users/<user_id>/sessions', methods=['POST'])
@token_required
def create_session(user_id):
    try:

        if not request.json or 'session_name' not in request.json:
            return jsonify({
                'error_code': 400,
                'description': "Missing message in request body",
            }), 400
        
        session_name = request.json['session_name']
        session_service = SessionService(g.db)
        new_session = session_service.add_session(session_name=session_name, user_id=user_id)
        
        return jsonify({
            'session_id': new_session.session_id,
            'session_name': new_session.session_name,
            'user_id': new_session.user_id
        }), 201
    except Exception as ex:
        g.excep = ex
        logging.error(f'Error in create_session {ex} ')
        return jsonify({
            'error_code': 500,
            'description': "Internal server error ",
        }), 500

# GET /users/<userId>/sessions -> List all sessions for a user
@app.route('/users/<user_id>/sessions', methods=['GET'])
@token_required
def get_user_sessions(user_id):
    try:
        session_service = SessionService(g.db)
        sessions =  session_service.get_sessions_by_user(user_id) 
        session_list = [{
            'session_id': session.session_id,
            'session_name': session.session_name
        } for session in sessions]
        
        return jsonify(session_list), 200
    except Exception as ex:
        g.excep = ex
        logging.error(f'Error in get_user_sessions {ex} ')
        return jsonify({
            'error_code': 500,
            'description': "Internal server error",
        }), 500


@app.route('/v2/users/<user_id>/sessions/<session_id>/chat', methods=['POST'])
@token_required
def makeTransactionEvent(user_id, session_id):
    try:

        if not request.json or 'message' not in request.json:
            return jsonify({
                'error_code': 400,
                'description': "Missing message in request body",
            }), 400
        
        prompt_req = request.json['message']
        event_info = extract_command_info(prompt_req)  # assuming this returns a dictionary
        logging.error(f"requested event : {event_info}")

        if event_info.get('operation') == "invalid_commnad":
            return jsonify({
                'error_code': 400,
                'description': f"Invalid command. Here is the available commands.",
            }), 400

        prompt_res = ""
        transaction_info = None
        user_servce = UserService(g.db)
        transaction_service = TransactionService(g.db)
        event_service = EventService(g.db)
        if event_info.get('operation') == "add":
            try:
                transaction_info = transaction_service.add_transaction(
                    session_id=session_id, 
                    operation=event_info.get('action'), 
                    amount=event_info.get('amount'), 
                    category=event_info.get('category'), 
                    sub_category=event_info.get('sub_category'), 
                    date_of_transaction=event_info.get('date')
                )
                prompt_res = f'Recorded {event_info.get("action")} of {event_info.get("amount")} on {event_info.get("category")}'
                new_event = event_service.add_event(
                    session_id=session_id, 
                    prompt_req=prompt_req, 
                    prompt_res=prompt_res, 
                    transaction_id=None if transaction_info is None else transaction_info.transaction_id)

                return jsonify({
                    'event_id': new_event.event_id,
                    'session_id': new_event.session_id,
                    'prompt_req': new_event.prompt_req,
                    'prompt_res': new_event.prompt_res,
                    'transaction_id': None if transaction_info is None else transaction_info.transaction_id
                }), 201
            except Exception as e:
                return jsonify({
                    'error_code': 500,
                    'description': f"Error while processing add operation: {str(e)}",
                }), 500
        elif event_info.get('operation') == "get":
            if event_info.get('action') == 'total':
                if event_info.get('report_type') == 'all' or event_info.get('report_type') is None:
                    total_amt_expense = transaction_service.get_total(session_id, 'expense', event_info.get('period'), event_info.get('date'))
                    total_amt_income = transaction_service.get_total(session_id,'income', event_info.get('period'), event_info.get('date'))

                    prompt_res = f'For {event_info.get("period")}, Total Income: {total_amt_income}, Total Expense: {total_amt_expense}'
                else:
                    total_amt = transaction_service.get_total(session_id, event_info.get('report_type'), event_info.get('period'), event_info.get('date'))
                    prompt_res = f'For {event_info.get("period")}, Total {event_info.get("report_type")}: {total_amt}'
            elif event_info.get('action') == 'report':
                if event_info.get('report_type') == 'all' or event_info.get('report_type') is None:
                    transaction_list_expense = transaction_service.get_transaction_report(session_id, 'expense', event_info.get('period'), event_info.get('date'))
                    transaction_list_income = transaction_service.get_transaction_report(session_id, 'income', event_info.get('period'), event_info.get('date'))

                    formatted_income_str = format_transaction_report_html(transaction_list_income, event_info.get('period'), 'income')
                    formatted_expense_str = format_transaction_report_html(transaction_list_expense, event_info.get('period'), 'expense')
                    prompt_res = f'Transaction report will be sent to your email shortly.' 
                    
                    sendTransactionReportToUser(user_id, f'{formatted_income_str} <br></br> {formatted_expense_str}')
                else:
                    transaction_list = transaction_service.get_transaction_report(session_id, event_info.get('report_type'), event_info.get('period'), event_info.get('date'))
                    formatted_str = format_transaction_report_html(transaction_list, event_info.get('period'), event_info.get('report_type'))
                    sendTransactionReportToUser(user_id, f'{formatted_str}')
                    prompt_res = f'Transaction report will be sent to your email shortly.'

            return jsonify({
                
                'prompt_req': prompt_req,
                'prompt_res': prompt_res,
                
            }), 201
    
    except Exception as ex:
        g.excep = ex
        logging.error(f'Error in makeTransactionEvent {ex} ')
        return jsonify({
            'error_code': 500,
            'description': "Internal server error",
        }), 500                
    
    return jsonify({
            'error_code': 500,
            'description': "Internal server error",
        }), 500   
    
    

# GET /users/<userId>/sessions/<sessionId>/chat_events -> Get all events for a session
@app.route('/users/<user_id>/sessions/<session_id>/chat_events', methods=['GET'])
@token_required
def get_session_events(user_id, session_id):
    try:  
        event_service = EventService(g.db)
        events = event_service.get_events_by_session(session_id)
        
        event_list = [{
            'event_id': event.event_id,
            'prompt_req': event.prompt_req,
            'prompt_res': event.prompt_res,
            'created_date': event.created_date,
            'updated_date': event.updated_date
        } for event in events]
        
        return jsonify(event_list), 200
    except Exception as ex:
        g.excep = ex
        logging.error(f'Error in get_session_events {ex} ')
        return jsonify({
            'error_code': 500,
            'description': "Internal server error",
        }), 500  

def sendTransactionReportToUser(user_id: str, report_text: str):
    user_service = UserService(g.db)
    user = user_service.get_user(user_id)
    if not user is None:
        send_email(user.email_id, 'Transaction Report Copy', report_text)

def format_transaction_report(transactions, period: str, action: str):
    # Header for the report
    response = f"Here is your requested {action} report for the {period}:\n"
    response += "-" * 62 + "\n"
    response += f"| {'Date of Transaction':<20} | {'Category':<12} | {'Subcategory':<12} | {'Amount':<8} |\n"
    response += "-" * 62 + "\n"

    # Loop through transactions and append them to the response
    for transaction in transactions:
        date_of_transaction = transaction['date_of_transaction'].strftime('%Y-%m-%d')
        category = transaction['category']
        subcategory = "" if transaction['sub_category'] is None else transaction['sub_category'] 
        amount = transaction['amount']
        response += f"| {date_of_transaction:<20} | {category:<12} | {subcategory:<12} | {amount:<8} |\n"

    response += "-" * 62
    return response

# Run the Flask app
if __name__ == '__main__':
    initiate_scheduled_task()
    # app.run(ssl_context=('cert.pem', 'key.pem'),debug=False, port = 443, host="0.0.0.0")
    app.run(debug=False, port = 8080, host="0.0.0.0")