from contextlib import contextmanager
from typing import Any, Generator

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
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
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


Base = declarative_base()  # type: Any


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    name = Column(String(50), nullable=False)
    money = Column(String(50), nullable=False)

    def __repr__(self) -> str:
        return f'User {self.name}'


class History(Base):
    __tablename__ = 'history'
    id = Column(Integer(), primary_key=True)
    id_of_user = Column(String(50), ForeignKey('users.id'))
    action = Column(String(50), nullable=False)
    money = Column(String(50), nullable=False)
    crypto = Column(String(50), nullable=False)

    def __repr__(self) -> str:
        return f'{self.action}: {self.money} rubles, {self.crypto}'


class Values(Base):
    __tablename__ = 'values'
    id = Column(Integer(), primary_key=True)
    name = Column(String(50), nullable=False)
    value = Column(String(50), nullable=False)

    def __repr__(self) -> str:
        return f'{self.name}'


class Balances(Base):
    __tablename__ = 'balances'
    id = Column(Integer(), primary_key=True)
    username = Column(String(50), nullable=False)
    cryptoname = Column(String(50), nullable=False)
    value = Column(String(50), nullable=False)

    def __repr__(self) -> str:
        return f'{self.cryptoname}: {self.value}'
