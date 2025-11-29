from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

url = 'sqlite:///./books.db'

engine = create_engine(url, connect_args={'check_same_thread':False}, future= True)

SessionLocal = sessionmaker(bind= engine, autoflush= False, autocommit = False)


class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

