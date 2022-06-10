from typing import Dict

from app.database import FightHistory, Turret, User, create_session
from app.guild import NO_GUILD
from app.new_user import make_bot


def fight(user1: User, user2: User) -> Dict[str, str]:
    """
    Calculates results of fights between user1 and user2,
    changes values in database (depends on fight result)
    :param user1: User_d object with information about P1
    :param user2: User_d object with information about P2
    :return: result of fight
    """
    with create_session() as session:
        power_from_tower = session.query(Turret).all()
        user1_power = user1.army_power
        user2_power = user2.army_power + power_from_tower[user2.turret_level - 1].power
        if user1_power > user2_power:
            money_transfered = user2.money // 10
            food_transfered = user2.food // 10
            user1.money += money_transfered
            user1.food += food_transfered
            user2.money -= money_transfered
            user2.food -= food_transfered
            user2.soldiers_t1 = 0
            user2.soldiers_t2 = 0
            user2.soldiers_t3 = 0
            user2.soldiers_t4 = 0
            user2.soldiers_t5 = 0
            user2.all_power -= user2.army_power
            user2.army_power = 0
            user1.rating += 10
            user2.rating = max(0, user2.rating - 10)
            fight_history = FightHistory(
                event='attack',
                player1=user1.login,
                player2=user2.login,
                result='victory',
            )
            session.add(fight_history)
            fight_history = FightHistory(
                event='defense',
                player1=user2.login,
                player2=user1.login,
                result='defeat',
            )
            session.add(fight_history)
            session.commit()
            return {
                'result': 'won',
                'money': money_transfered,
                'food': food_transfered,
                'rating': '+10',
            }
        if user2_power > user1_power:
            user1.soldiers_t1 = 0
            user1.soldiers_t2 = 0
            user1.soldiers_t3 = 0
            user1.soldiers_t4 = 0
            user1.soldiers_t5 = 0
            user1.all_power -= user1.army_power
            user1.army_power = 0
            session.commit()
            user2.rating += 10
            user1.rating = max(0, user1.rating - 10)
            fight_history = FightHistory(
                event='attack',
                player1=user1.login,
                player2=user2.login,
                result='defeat',
            )
            session.add(fight_history)
            fight_history = FightHistory(
                event='defense',
                player1=user2.login,
                player2=user1.login,
                result='victory',
            )
            session.add(fight_history)
            return {'result': 'lost', 'rating': '-10'}
        user1.rating += 1
        user2.rating += 1
        fight_history = FightHistory(
            event='attack', player1=user1.login, player2=user2.login, result='draw'
        )
        session.add(fight_history)
        fight_history = FightHistory(
            event='attack', player1=user2.login, player2=user1.login, result='draw'
        )
        session.add(fight_history)
        session.commit()
        return {'result': 'draw', 'rating': '+1'}


def attack(user_to_attack: str, username: str) -> Dict[str, str]:
    """
    Attack another player
    :param user_to_attack: target's nickname
    :param username: user that tries to attack
    :return: result of attack
    """
    with create_session() as session:
        if username == user_to_attack:
            return {'error': 'you cannot attack yourself!'}
        user_query = session.query(User.id).filter(User.login == user_to_attack)
        if session.query(user_query.exists()).scalar():
            user1 = session.query(User).filter(User.login == username).one()
            user2 = session.query(User).filter(User.login == user_to_attack).one()
            if abs(user1.rating - user2.rating) > 100:
                return {'error': 'difference between ratings is too big (>100)'}
            if user1.guild == user2.guild and user1.guild != NO_GUILD:
                return {'error': 'you cannot attack a player from your guild!'}
            return fight(user1, user2)
        return {'error': 'no user found'}


def attack_b(username: str, level: int) -> Dict[str, str]:
    """
    Attack bot
    :param username: user that tries to attack
    :param level: bot's level(1-5)
    :return: result of attack
    """
    with create_session() as session:
        user1 = session.query(User).filter(User.login == username).one()
        user2 = make_bot(level)
        return fight(user1, user2)
