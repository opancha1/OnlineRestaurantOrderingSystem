from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import conf
from urllib.parse import quote_plus

# URL-encode the password to safely handle special characters like "@"
password = quote_plus(conf.db_password)

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{conf.db_user}:{password}"
    f"@{conf.db_host}:{conf.db_port}/{conf.db_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
