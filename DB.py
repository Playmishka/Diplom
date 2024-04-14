from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DB_PATH

engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()
