import re
import datetime


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