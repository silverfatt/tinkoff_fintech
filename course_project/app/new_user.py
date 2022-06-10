from app.database import Soldier, User, create_session
from app.guild import NO_GUILD


def make_new_user(login: str, password: str) -> User:
    """
    Generates new user
    :param login: new user's login
    :param password: new user's password
    :return: generated user
    """
    user = User(
        guild=NO_GUILD,
        rank='member',
        rating=0,
        login=login,
        money=0,
        food=0,
        password=password,
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


def make_bot(level: int) -> User:
    """
    Generates bot
    :param level: level of bot
    :return: generated bot
    """
    with create_session() as session:
        soldiers = session.query(Soldier).all()
        army_power = 0
        for i in range(5):
            army_power += soldiers[i].power * level * (4 - i)
        all_power = 500 + army_power
        bot = User(
            guild=NO_GUILD,
            rank='member',
            rating=0,
            login='bot',
            money=1000 * level,
            food=1000 * level,
            password='1234',
            buildings_power=500,
            army_power=army_power,
            all_power=all_power,
            HQ_level=1,
            Miner1_level=1,
            Miner2_level=1,
            Wh_level=1,
            turret_level=1,
            soldiers_t1=level * 5,
            soldiers_t2=level * 4,
            soldiers_t3=level * 3,
            soldiers_t4=level * 2,
            soldiers_t5=level * 1,
        )
        return bot
