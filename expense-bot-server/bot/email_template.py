from datetime import datetime


def format_transaction_report_html(transactions, period: str, action: str):
  
    # Define basic styles
    styles = """
    <style>
        body {
            font-family: Arial, sans-serif;
            color: #333333;
        }
        .report-container {
            width: 100%;
            max-width: 800px;
            margin: auto;
        }
        .report-header {
            text-align: center;
            padding: 20px 0;
        }
        .report-title {
            font-size: 24px;
            margin-bottom: 10px;
        }
        .report-period {
            font-size: 18px;
            color: #555555;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 12px;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #fafafa;
        }
        .footer {
            text-align: center;
            font-size: 14px;
            color: #777777;
            margin-top: 20px;
        }
    </style>
    """

    # Start building the HTML content
    html = f"""
    <html>
    <head>
        {styles}
    </head>
    <body>
        <div class="report-container">
            <div class="report-header">
                <div class="report-title">{action.capitalize()} Report</div>
                <div class="report-period">for the {period}</div>
            </div>
            <table>
                <tr>
                    <th>Date of Transaction</th>
                    <th>Category</th>
                    <th>Subcategory</th>
                    <th>Amount</th>
                </tr>
    """

    # Add transaction rows
    for transaction in transactions:
        date_of_transaction = transaction['date_of_transaction'].strftime('%Y-%m-%d') if isinstance(transaction['date_of_transaction'], datetime) else transaction['date_of_transaction']
        category = transaction['category'] or "N/A"
        subcategory = transaction['sub_category'] or "N/A"
        amount = f"{float(transaction['amount']):,.2f}"
        html += f"""
                <tr>
                    <td>{date_of_transaction}</td>
                    <td>{category}</td>
                    <td>{subcategory}</td>
                    <td>{amount}</td>
                </tr>
        """

    # Close the table and add footer
    html += """
            </table>
            <div class="footer">
                Thank you for using our Expense Tracker Service!
            </div>
        </div>
    </body>
    </html>
    """

    return html