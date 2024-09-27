import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import logging

# Load environment variables from the .env file
load_dotenv()

smtp_server = os.getenv('SMTP_SERVER')
smtp_port = os.getenv('SMTP_PORT')
smtp_user = os.getenv('SMTP_USER')
smtp_pass = os.getenv('SMTP_PASS')
sender_email = os.getenv('SMTP_SENDER')

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Define the format
)
# Create a logger object
logger = logging.getLogger(__name__)

def send_email(receiver_email, subject, message_body):
    try:
        # Create a multipart message and set headers
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Add body to the email
        msg.attach(MIMEText(message_body, 'html'))

        # Connect to the server and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(smtp_user, smtp_pass)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        logger.info(f"Email sent to {receiver_email} successfully!")
    except Exception as e:
        logger.error(f"Error sending email: {e}")