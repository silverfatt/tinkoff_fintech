from typing import Dict

from app.database import (
    FightHistory,
    FoodMiner,
    MoneyMiner,
    Soldier,
    User,
    create_session,
)


def get_fight_h(username: str) -> Dict[str, str]:
    """
    Get dictionary with all username's fights and results
    :param username: user who tries to get history
    :return: dictionary with fight history
    """
    with create_session() as session:
        fight_history = (
            session.query(FightHistory).filter(FightHistory.player1 == username).all()
        )
        events_dictionary = {
            fight.event: f'{fight.player1} vs {fight.player2}, {fight.result}'
            for fight in fight_history
        }
        return events_dictionary


def get_economy_information(username: str) -> Dict[str, str]:
    """
    Get detailed information about username's economy
    :param username: user who tries to get information
    :return: dictionary with all information
    """
    with create_session() as session:
        soldiers = session.query(Soldier).all()
        moneymines = session.query(MoneyMiner).all()
        foodmines = session.query(FoodMiner).all()
        user = session.query(User).filter(User.login == username).one()
        food_income = foodmines[user.Miner2_level - 1].performance
        food_outcome = (
            soldiers[0].food_to_keep * user.soldiers_t1
            + soldiers[1].food_to_keep * user.soldiers_t2
            + soldiers[2].food_to_keep * user.soldiers_t3
            + soldiers[3].food_to_keep * user.soldiers_t4
            + soldiers[4].food_to_keep * user.soldiers_t5
        )
        return {
            'money': user.money,
            'food': user.food,
            'money income': moneymines[user.Miner1_level - 1].performance,
            'food summary income': food_income - food_outcome,
            'food income': food_income,
            'food outcome (from soldiers)': food_outcome,
        }


def get_profile_info(username: str) -> Dict[str, str]:
    """
    Get full information about username's stats: resources,
    guild, buildings, etc.
    :param username: user who tries to get information
    :return: dictionary with all information
    """
    with create_session() as session:
        user = session.query(User).filter_by(login=username).first()
        return user.get_user_info()
