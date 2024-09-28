import re
from datetime import datetime,timedelta




def extract_command_info(command):
    add_pattern = r"^add (e|expense|i|income) (\d+\.\d+|[\d]+) (([\w]+)(?: ([\w\s]+))?)?\s*((\d{4})|(\d{4}[-|\/]\d{2}[-|\/]\d{2})|(\d{2}[-|\/]\d{2}[-|\/]\d{4}))?$"
    get_pattern = r"^get (report|total) (day|month|year) ((\d{4})|(\d{4}[-|\/]\d{2}[-|\/]\d{2})|(\d{2}[-|\/]\d{2}[-|\/]\d{4}))?\s?(expense|income|all)$"
    
    try:
        if command.startswith("get"):
            operation = "get"
            match = re.match(get_pattern, command)
            
            if match.group(1) == 'e':
                action = 'expense'
            elif match.group(1) == 'i':
                action = 'income'
            else:
                action = match.group(1)

            period = match.group(2)
            date_str = match.group(4) or match.group(5) or match.group(6)
            report_type = match.group(7)

            if date_str:
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d" if len(date_str) == 10 else "%Y")
            else:
                date = datetime.datetime.today()

            return {
                "operation": operation,
                "action": action,
                "period": period,
                "date": date,
                "report_type": report_type
            }
        elif command.startswith("add"):
            operation = "add"
            match = re.match(add_pattern, command)
            if match.group(1) == 'e':
                action = 'expense'
            elif match.group(1) == 'i':
                action = 'income'
            else:
                action = match.group(1)
        
            amount = match.group(2)
            category = match.group(4)
            subcategory = match.group(5)
            date_str = match.group(6) or match.group(7) or match.group(8)

            if date_str:
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d" if len(date_str) == 10 else "%Y")
            else:
                date = datetime.datetime.now()
        else:
            return {
                "operation": "invalid_commnad"
            }

        return {
            "operation": operation,
            "action": action,
            "amount": amount,
            "category": category,
            "subcategory": subcategory,
            "date": date
        } 
        
    except:
        return {
            "operation": "invalid_commnad"
        }



# Define keywords and patterns
expense_keywords = ['log expense', 'add expense', 'record expense', 'expense add', 'add e', 'log', 'expense', 'record', 'spend', 'spent']
income_keywords = ['add income', 'got income', 'received income', 'add i', 'income', 'received', 'earned', ' i ']
prepositions = ['on', 'of', 'for', 'with', 'at', 'by', 'about', 'through', 'over', 'to', 'a', 'an', 'the', 'and', 'or', 'but', 'from', 'got']
date_patterns = [r'\b\d{2}/\d{2}/\d{4}\b', r'\b\d{2}-\d{2}-\d{4}\b', r'\b\d{4}/\d{2}/\d{2}\b', r'\b\d{4}-\d{2}-\d{2}\b', r'\btoday\b', r'\byesterday\b']
get_action_dict = {"total": ["total", "balance", "show", "get", "check"], "report": ["report", "generate", "show report", "get report"]}
period_dict = {"day": ["today", "day", "daily"], "month": ["this month", "month", "monthly"], "year": ["this year", "year", "yearly"]}
report_type_dict = {"expense": ["expense", "spent", "expenses"], "income": ["income", "earnings"]}

# Helper functions
def remove_prepositions(text):
    words = text.split() 
    cleaned_words = [word for word in words if word not in prepositions]
    return ' '.join(cleaned_words)

def get_action(text):
    text_lower = text.lower()
    for action, keywords in get_action_dict.items():
        for keyword in keywords:
            if keyword in text:
                return action, keyword
    
    for keyword in expense_keywords:
        if keyword in text_lower:
            return 'expense', keyword

    for keyword in income_keywords:
        if keyword in text_lower:
            return 'income', keyword
    
    return None, None

def get_amount(text):
    match = re.search(r'\d+(\.\d{1,2})?', text)
    return match.group() if match else None

def remove_extra_keywords(text):
    words = text.split()
    cleaned_words = [word for word in words if word not in expense_keywords + income_keywords]
    return ' '.join(cleaned_words)

date_patterns = [
    r'\b\d{2}/\d{2}/\d{4}\b',  # Matches dates like 25/12/2023
    r'\b\d{2}-\d{2}-\d{4}\b',  # Matches dates like 25-12-2023
    r'\b\d{4}/\d{2}/\d{2}\b',  # Matches dates like 2023/12/25
    r'\b\d{4}-\d{2}-\d{2}\b',  # Matches dates like 2023-12-25
    r'\btoday\b',               # Matches 'today'
    r'\byesterday\b'            # Matches 'yesterday'
]

def get_date(text):
    text_lower = text.lower()
    
    for pattern in date_patterns:
        match = re.search(pattern, text_lower)
        
        if match:
            date_str = match.group()
            
            # Handle "today" and "yesterday"
            if date_str == 'today':
                return datetime.now(), re.sub(r'\btoday\b', '', text)
            elif date_str == 'yesterday':
                return datetime.now() - timedelta(days=1), re.sub(r'\byesterday\b', '', text)
            else:
                # Attempt to parse the date string into a datetime object
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%Y-%m-%d']:
                    try:
                        return datetime.strptime(date_str, fmt), text.replace(date_str, '')
                    except ValueError:
                        continue
    # Default to current date if no match is found
    return datetime.now(), text

def get_category(text, actual_keyword):
    cleaned_text = text.lower().replace(actual_keyword, '')
    cleaned_text = re.sub(r'\d+(\.\d{1,2})?', '', cleaned_text)
    return cleaned_text.strip()


def detect_period(command):
    for period, keywords in period_dict.items(): 
        for keyword in keywords:
            if keyword in command:
                return period
    return "all"

def detect_report_type(command):
    for report_type, keywords in report_type_dict.items():
        for keyword in keywords:
            if keyword in command:
                return report_type
    return "all"

# Main function to process the input command
def extract_process_command(command):
    try:
        sanitized_command = remove_prepositions(command.lower())
        action, actual_keyword = get_action(sanitized_command)
        if action in ['total', 'report']:
            period = detect_period(sanitized_command)
            date = get_date(sanitized_command)[0]
            report_type = detect_report_type(sanitized_command)
        
            return {
                "operation": 'get',
                "action": action,
                "period": period,
                "date": date,
                "report_type": report_type
            }
        elif action in ['expense', 'income']:
            amount = get_amount(sanitized_command)
            if not amount:
                raise Exception("Error: Could not extract the amount.")

            sanitized_command = remove_extra_keywords(sanitized_command)
            date, sanitized_command = get_date(sanitized_command)
            category = get_category(sanitized_command, actual_keyword)

            return {
                'operation': 'add',
                'action': action,
                'amount': amount,
                'category': category,
                'date': date
            } 
        else:  
            return {
                "operation": "invalid_commnad"
            }
    except Exception as ex:
        return {
            "operation": "invalid_commnad"
        }

    
        

if __name__ == '__main__':
    commands = [
        "spent 1000 on groceries",
        "add expense of 200 for rent with utilities",
        "log an expense of 1500 on dining",
        "received income of 3000 from salary",
        "record expense of 200 for transport and fuel",
        "add e for shopping and dining of 3000 01-07-2023",
       "total",
       "total expenes"
    ]

    for command in commands:
        result = process_command(command)
        print(f"Command: {command} -> Extracted Info: {result}")