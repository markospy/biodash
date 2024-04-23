import smtplib
from random import randint

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from templates.email import EMAIL_HTML_TEMPLATE
from env_loader import EnvLoader

env_loader = EnvLoader()

class EmailSenderClass:
    def __init__(self):
        """ """
        self.logaddr = env_loader.from_address
        self.fromaddr = env_loader.from_address
        self.password = env_loader.password_google

    def sendMessageViaServer(self, toaddr, msg):
        # Send the message via local SMTP server.
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(self.logaddr, self.password)
        text = msg.as_string()
        server.sendmail(self.fromaddr, toaddr, text)
        server.quit()

    def sendHtmlEmailTo(self, destName, destinationAddress, code):
        # Message setup
        msg = MIMEMultipart()

        msg["From"] = "Support<" + self.fromaddr + ">"
        msg["To"] = destinationAddress
        msg["Subject"] = "BioDash. Email verification."

        txt = EMAIL_HTML_TEMPLATE.format(destName, code)

        # Add text to message
        msg.attach(MIMEText(txt, "html"))

        print("Send email from {} to {}".format(self.fromaddr, destinationAddress))
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
    email_msg.sendHtmlEmailTo(name, email, code)
    print(code)
    return code