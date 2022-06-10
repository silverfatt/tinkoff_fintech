import time

from app.database import FoodMiner, MoneyMiner, Soldier, User, Warehouse, create_session


def run_background_calculations() -> None:  # pragma: no cover
    """
    Makes mines to work and soldiers to eat every 10 seconds
    """
    while True:  # pragma: no cover
        time.sleep(10)
        with create_session() as session:
            users = session.query(User).all()
            soldiers = session.query(Soldier).all()
            money_to_add = session.query(MoneyMiner).all()
            food_to_add = session.query(FoodMiner).all()
            warehouses = session.query(Warehouse).all()
            for user in users:  # pragma: no cover
                user.money = min(
                    user.money + money_to_add[user.Miner1_level - 1].performance,
                    warehouses[user.Wh_level - 1].capacity,
                )
                user.food = min(
                    user.food + food_to_add[user.Miner2_level - 1].performance,
                    warehouses[user.Wh_level - 1].capacity,
                )
                food_usage = (
                    user.soldiers_t1 * soldiers[0].food_to_keep
                    + user.soldiers_t2 * soldiers[1].food_to_keep
                    + user.soldiers_t3 * soldiers[2].food_to_keep
                    + user.soldiers_t4 * soldiers[3].food_to_keep
                    + user.soldiers_t5 * soldiers[4].food_to_keep
                )
                user.food = max(user.food - food_usage, 0)
            session.commit()
