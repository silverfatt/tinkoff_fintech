from contextlib import contextmanager
from typing import Any, Dict, Generator

from sqlalchemy import Column, Integer, String, Text, create_engine
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


def prepare_db() -> None:
    with create_session() as session:
        headquarters_query = session.query(HQ.id).filter(HQ.power == 100)
        if not session.query(headquarters_query.exists()).scalar():
            for i in range(1, 6):
                headquarters = HQ(
                    power=100 * i**3,
                    current_level=1 * i,
                    money_to_upgrade=100 * i**2,
                )
                miner1 = MoneyMiner(
                    power=100 * i,
                    current_level=1 * i,
                    performance=150 * i,
                    money_to_upgrade=100 * i * 2,
                )
                miner2 = FoodMiner(
                    power=100 * i,
                    current_level=1 * i,
                    performance=150 * i,
                    money_to_upgrade=100 * i * 2,
                )
                warehouse = Warehouse(
                    power=100 * i,
                    current_level=1 * i,
                    capacity=1000 * i,
                    money_to_upgrade=100 * i,
                )
                turret = Turret(
                    power=100 * i, current_level=1 * i, money_to_upgrade=100 * i
                )
                soldier = Soldier(
                    power=2 * i, level=1 * i, money_to_hire=5 * i, food_to_keep=1 * i
                )
                session.add(headquarters)
                session.add(miner1)
                session.add(miner2)
                session.add(warehouse)
                session.add(turret)
                session.add(soldier)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    guild = Column(String(50), nullable=False)
    rank = Column(String(50), nullable=False)
    rating = Column(Integer(), nullable=False)
    login = Column(String(50), nullable=False)
    money = Column(Integer(), nullable=False)
    food = Column(Integer(), nullable=False)
    password = Column(Integer(), nullable=False)
    buildings_power = Column(Integer(), nullable=False)
    army_power = Column(Integer(), nullable=False)
    all_power = Column(Integer(), nullable=False)
    HQ_level = Column(Integer(), nullable=False)
    Miner1_level = Column(Integer(), nullable=False)
    Miner2_level = Column(Integer(), nullable=False)
    Wh_level = Column(Integer(), nullable=False)
    turret_level = Column(Integer(), nullable=False)
    soldiers_t1 = Column(Integer(), nullable=False)
    soldiers_t2 = Column(Integer(), nullable=False)
    soldiers_t3 = Column(Integer(), nullable=False)
    soldiers_t4 = Column(Integer(), nullable=False)
    soldiers_t5 = Column(Integer(), nullable=False)

    def __repr__(self) -> str:
        return f'User {self.login}, password: {self.password}'

    def get_user_info(self) -> Dict[str, str]:
        return {
            'user': self.login,
            'guild': self.guild,
            'rank': self.rank,
            'rating': self.rating,
            'Money': self.money,
            'Food': self.food,
            'Army power': self.army_power,
            'Buildings power': self.buildings_power,
            'All power': self.all_power,
            'HQ level': self.HQ_level,
            'Miner1 level': self.Miner1_level,
            'Miner2 level': self.Miner2_level,
            'Wh level': self.Wh_level,
            'Turret level': self.turret_level,
            'Soldiers tier1': self.soldiers_t1,
            'Soldiers tier2': self.soldiers_t2,
            'Soldiers tier3': self.soldiers_t3,
            'Soldiers tier4': self.soldiers_t4,
            'Soldiers tier5': self.soldiers_t5,
        }


class HQ(Base):
    __tablename__ = 'HQ'
    id = Column(Integer(), primary_key=True)
    power = Column(Integer(), nullable=False)
    current_level = Column(Integer(), nullable=False)
    money_to_upgrade = Column(Integer(), nullable=False)


class MoneyMiner(Base):
    __tablename__ = 'MoneyMiner'
    id = Column(Integer(), primary_key=True)
    power = Column(Integer(), nullable=False)
    performance = Column(Integer(), nullable=False)
    current_level = Column(Integer(), nullable=False)
    money_to_upgrade = Column(Integer(), nullable=False)


class FoodMiner(Base):
    __tablename__ = 'FoodMiner'
    id = Column(Integer(), primary_key=True)
    power = Column(Integer(), nullable=False)
    performance = Column(Integer(), nullable=False)
    current_level = Column(Integer(), nullable=False)
    money_to_upgrade = Column(Integer(), nullable=False)


class Warehouse(Base):
    __tablename__ = 'Warehouse'
    id = Column(Integer(), primary_key=True)
    power = Column(Integer(), nullable=False)
    current_level = Column(Integer(), nullable=False)
    capacity = Column(Integer(), nullable=False)
    money_to_upgrade = Column(Integer(), nullable=False)


class Turret(Base):
    __tablename__ = 'Turret'
    id = Column(Integer(), primary_key=True)
    power = Column(Integer(), nullable=False)
    current_level = Column(Integer(), nullable=False)
    money_to_upgrade = Column(Integer(), nullable=False)


class Soldier(Base):
    __tablename__ = 'soldiers'
    id = Column(Integer(), primary_key=True)
    level = Column(Integer(), nullable=False)
    power = Column(Integer(), nullable=False)
    money_to_hire = Column(Integer(), nullable=False)
    food_to_keep = Column(Integer(), nullable=False)

    def __repr__(self) -> str:
        return f'Building {self.name} {self.power} {self.level} {self.money_to_hire}'


class Guild(Base):
    __tablename__ = 'guilds'
    id = Column(Integer(), primary_key=True)
    name = Column(String(50), nullable=False)


class FightHistory(Base):
    __tablename__ = 'fights'
    id = Column(Integer(), primary_key=True)
    event = Column(String(50), nullable=False)
    player1 = Column(String(50), nullable=False)
    player2 = Column(String(50), nullable=False)
    result = Column(String(50), nullable=False)


class GuildNotes(Base):
    __tablename__ = 'notes'
    id = Column(Integer(), primary_key=True)
    sender = Column(String(50), nullable=False)
    guildname = Column(String(50), nullable=False)
    text = Column(Text(), nullable=False)
