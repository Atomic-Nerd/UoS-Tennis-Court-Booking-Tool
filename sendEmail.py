import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

def send_email_booked(email, park, date, time, court, code):
    load_dotenv()
    gmail_pass = os.getenv('gmail_pass')

    msg = EmailMessage()
    msg["From"] = "jonathanashworth101@gmail.com"
    msg["To"] = email
    msg["Subject"] = "UoS Tennis Court Booking"
    msg.set_content(f"Hi, \n\nFor your upcoming court booking, the code is as follows:\n{park}, {date}, {time}, Court {court} - {code}\n\nIf you have any questions or issues on the day, please don't hesitate to contact me. I hope you enjoy your session!\n\nKind regards,\nJonny")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("jonathanashworth101@gmail.com", gmail_pass)
            smtp.send_message(msg)
        
        return True 
    except Exception as e:
        return False 