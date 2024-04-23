from sqlalchemy.orm import DeclarativeBase, sessionmaker

from env_loader import EnvLoader
from models.engine import create_engine_from_user_choice, DatabaseConfig

env_loader = EnvLoader()

class Base(DeclarativeBase):
    pass

# Creation of the engine
database_config = DatabaseConfig(env_loader.user, env_loader.password, env_loader.host, env_loader.port, env_loader.database)
engine = create_engine_from_user_choice("sqlite", database_config)

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(engine)