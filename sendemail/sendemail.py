import sys
import os
import smtplib
from random import randint

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()
from_address = os.getenv("EMAIL")
password = os.getenv("PASSWORD_GOOGLE")

EMAIL_HTML_TEMPLATE = """
<html>
<head>
</head>
<body>
    <p style ="margin: 5px 0;line-height: 25px; font-size: 16px;"><h2>Hello, {}!</h2><br>
    <br>
    We are happy that you use our application.
    <br>
    This verification code can be used at any time unless you request another one.
    In this case it will lose validity and only the most recent one will be valid.
    <br>
    {}
    <br>
    <h2>
    {}
    </h2>
    Bye!
    <br>
    </p>
</body>
</html>
"""


class EmailSenderClass:
    def __init__(self):
        """ """
        self.logaddr = from_address  # username
        self.fromaddr = from_address  # from address
        self.password = password  # password app

    def sendMessageViaServer(self, toaddr, msg):
        # Send the message via local SMTP server.
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(self.logaddr, self.password)
        text = msg.as_string()
        server.sendmail(self.fromaddr, toaddr, text)
        server.quit()

    def sendHtmlEmailTo(self, destName, destinationAddress, msgBody, code):
        # Message setup
        msg = MIMEMultipart()

        msg["From"] = "Support<" + self.fromaddr + ">"
        msg["To"] = destinationAddress
        msg["Subject"] = "BioDash. Email verification."

        txt = EMAIL_HTML_TEMPLATE

        txt = txt.format(destName, msgBody, code)

        # Add text to message
        msg.attach(MIMEText(txt, "html"))

        print(
            "Send email from {} to {}".format(self.fromaddr, destinationAddress)
        )
        self.sendMessageViaServer(destinationAddress, msg)


def send_email(name: str, email: str) -> int:
    """Send a verification code to the user's email and return the code

    Args:
        name (str): User's name
        email (str): User's email

    Returns:
        int: Verification code
    """
    code = randint(10_000, 99_999)
    email_msg = EmailSenderClass()
    email_msg.sendHtmlEmailTo(name, email, "Verification code:", code)
    return code
