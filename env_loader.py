import os
from dotenv import load_dotenv

# Objeto para cargar variables de entornos

class EnvLoader:
    def __init__(self):
        load_dotenv()
        self.user = os.getenv("USER")
        self.password= os.getenv("PASSWORD")
        self.host = os.getenv("HOST")
        self.port = os.getenv("PORT")
        self.database = os.getenv("BD")
        self.from_address = os.getenv("EMAIL")
        self.password_google = os.getenv("PASSWORD_GOOGLE")
        self.secrete_key = os.getenv("SECRET_KEY")
        self.algorithm = os.getenv("ALGORITHM")
        self.acces_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))