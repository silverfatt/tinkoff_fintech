import pytest

from app.database import Base, Guild, User, create_engine, prepare_db, sessionmaker

engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)


@pytest.fixture()
def default_user1():
    user = User(
        login='User1',
        guild='%_no_guild_%',
        money=0,
        food=0,
        rank='member',
        rating=0,
        password='123',
        buildings_power=500,
        army_power=20,
        all_power=520,
        HQ_level=1,
        Miner1_level=1,
        Miner2_level=1,
        Wh_level=1,
        turret_level=1,
        soldiers_t1=10,
        soldiers_t2=0,
        soldiers_t3=0,
        soldiers_t4=0,
        soldiers_t5=0,
    )
    return user


@pytest.fixture()
def default_user2():
    user = User(
        login='User2',
        guild='%_no_guild_%',
        money=0,
        food=0,
        rank='member',
        rating=0,
        password='123',
        buildings_power=500,
        army_power=20,
        all_power=520,
        HQ_level=1,
        Miner1_level=1,
        Miner2_level=1,
        Wh_level=1,
        turret_level=1,
        soldiers_t1=10,
        soldiers_t2=0,
        soldiers_t3=0,
        soldiers_t4=0,
        soldiers_t5=0,
    )
    return user


@pytest.fixture()
def default_guild():
    guild = Guild(name='default')
    return guild


@pytest.fixture(autouse=True)
def __init__db():
    Base.metadata.create_all(engine)
    prepare_db()
    yield
    Base.metadata.drop_all(engine)
