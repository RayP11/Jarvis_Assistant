import smtplib
import os
from dotenv import load_dotenv
import ssl
from email.message import EmailMessage
from openaiAPI import Create_Jarvis,messages

load_dotenv()

email_sender = "jarvis.r11510@gmail.com" 
email_password = os.getenv("EMAIL_PASSWORD")
email_receiver = os.getenv("PHONE_NUMBER")

def sendText(message):

    messages.append({"role": "user", "content": message + " make a very short message for me based on the following. MAKE IT VERY BRIEF and to the POINT"})
    response = Create_Jarvis(messages)

    body= response

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
