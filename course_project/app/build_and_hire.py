from typing import Dict

from app.database import (
    HQ,
    FoodMiner,
    MoneyMiner,
    Soldier,
    Turret,
    User,
    Warehouse,
    create_session,
)
from app.schemas import TierScheme


def up_building(building_form: TierScheme, username: str) -> Dict[str, str]:
    """
    Upgrade building. 1 - HQ, 2 - MoneyMiner, 3 - FoodMiner, 4 - Warehouse, 5 - Turret
    :param building_form: takes values from 1 to 5 - type of building
    :param username: user that tries to upgrade building
    :return: result of operation
    """
    with create_session() as session:
        user = session.query(User).filter(User.login == username).one()
        tier = building_form.tier
        if tier == 1:
            building = session.query(HQ).all()
            if user.money > building[user.HQ_level - 1].money_to_upgrade:
                if user.HQ_level == 5:
                    return {'result': 'max level reached'}
                user.HQ_level += 1
                user.buildings_power += (
                    building[user.HQ_level - 1].power
                    - building[user.HQ_level - 2].power
                )
                user.money -= building[user.HQ_level - 2].money_to_upgrade
            else:
                return {'result': 'not enough money'}
        elif tier == 2:
            building = session.query(MoneyMiner).all()
            if user.money > building[user.Miner1_level - 1].money_to_upgrade:
                if user.Miner1_level == 5:
                    return {'result': 'max level reached'}
                user.Miner1_level += 1
                user.buildings_power += (
                    building[user.Miner1_level - 1].power
                    - building[user.Miner1_level - 2].power
                )
                user.money -= building[user.Miner1_level - 2].money_to_upgrade
            else:
                return {'result': 'not enough money'}
        elif tier == 3:
            building = session.query(FoodMiner).all()
            if user.money > building[user.Miner2_level - 1].money_to_upgrade:
                if user.Miner2_level == 5:
                    return {'result': 'max level reached'}
                user.Miner2_level += 1
                user.buildings_power += (
                    building[user.Miner2_level - 1].power
                    - building[user.Miner2_level - 2].power
                )
                user.money -= building[user.Miner2_level - 2].money_to_upgrade
            else:
                return {'result': 'not enough money'}
        elif tier == 4:
            building = session.query(Warehouse).all()
            if user.money > building[user.Wh_level - 1].money_to_upgrade:
                if user.Wh_level == 5:
                    return {'result': 'max level reached'}
                user.Wh_level += 1
                user.buildings_power += (
                    building[user.Wh_level - 1].power
                    - building[user.Wh_level - 2].power
                )
                user.money -= building[user.Wh_level - 2].money_to_upgrade
            else:
                return {'result': 'not enough money'}
        elif tier == 5:
            building = session.query(Turret).all()
            if user.money > building[user.turret_level - 1].money_to_upgrade:
                if user.turret_level == 5:
                    return {'result': 'max level reached'}
                user.turret_level += 1
                user.buildings_power += (
                    building[user.turret_level - 1].power
                    - building[user.turret_level - 2].power
                )
                user.money -= building[user.turret_level - 2].money_to_upgrade
            else:
                return {'result': 'not enough money'}
        user.all_power = user.buildings_power + user.army_power
        session.commit()
        return {'result': 'success'}


def h_army(hiring_form: TierScheme, amount: int, username: str) -> Dict[str, str]:
    """
    Hire soldiers
    :param hiring_form: tier of soldiers (1-5)
    :param amount: amount of soldiers to hire
    :param username: user that tries to hire
    :return: result of operation
    """
    with create_session() as session:
        user = session.query(User).filter(User.login == username).one()
        hiring = hiring_form.tier
        soldier = session.query(Soldier).filter(Soldier.level == hiring).one()
        if user.money < soldier.money_to_hire * amount:
            return {'result': 'not enough money'}
        if user.HQ_level < hiring:
            return {'result': 'HQ level is too low'}
        if hiring == 1:
            user.soldiers_t1 += hiring * amount
        elif hiring == 2:
            user.soldiers_t2 += hiring * amount
        elif hiring == 3:
            user.soldiers_t3 += hiring * amount
        elif hiring == 4:
            user.soldiers_t4 += hiring * amount
        elif hiring == 5:
            user.soldiers_t5 += hiring * amount
        user.money -= soldier.money_to_hire * amount
        user.army_power += soldier.power * amount
        user.all_power += soldier.power * amount
        session.commit()
        return {'result': 'hired successfully'}
