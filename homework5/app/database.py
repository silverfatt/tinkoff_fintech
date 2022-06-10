from contextlib import contextmanager
from typing import Any, Generator

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)


@contextmanager
def create_session(
    **kwargs: dict[str, Any]
) -> Generator[Session, Any, Any]:  # pragma: no cover
    new_session = Session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except SQLAlchemyError:
        new_session.rollback()
        raise
    finally:
        new_session.close()


Base = declarative_base()  # type: Any


class User_d(Base):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    login = Column(String(50), nullable=False)
    password = Column(Integer(), nullable=False)

    def __repr__(self) -> str:
        return f'User {self.login}, password: {self.password}'


class Film_d(Base):
    __tablename__ = 'films'
    id = Column(Integer(), primary_key=True)
    title = Column(String(50), nullable=False)
    director = Column(String(50), nullable=False)
    release = Column(Integer(), nullable=False)
    average_rating = Column(String(3), nullable=False)


class Ratings_d(Base):
    __tablename__ = 'ratings'
    id = Column(Integer(), primary_key=True)
    title = Column(String(50), nullable=False)
    user = Column(String(50), nullable=False)
    rating = Column(Integer(), nullable=False)


class Reviews_d(Base):
    __tablename__ = 'reviews'
    id = Column(Integer(), primary_key=True)
    title = Column(String(50), nullable=False)
    user = Column(String(50), nullable=False)
    review = Column(Text(), nullable=False)
