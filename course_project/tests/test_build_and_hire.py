import pytest

from app.build_and_hire import h_army, up_building
from app.database import create_session
from app.schemas import TierScheme


class TestBuildAndHire:
    @pytest.mark.parametrize(
        'building',
        [1, 2, 3, 4, 5],
    )
    def test_up_building_with_no_money(self, building, default_user1):
        with create_session() as session:
            user1 = default_user1
            session.add(user1)
            session.commit()
            assert up_building(TierScheme(tier=building), default_user1.login) == {
                'result': 'not enough money'
            }

    @pytest.mark.parametrize(
        'building',
        [1, 2, 3, 4, 5],
    )
    def test_up_building_success(self, building, default_user1):
        with create_session() as session:
            user1 = default_user1
            user1.money = 10000000
            session.add(user1)
            session.commit()
            assert up_building(TierScheme(tier=building), default_user1.login) == {
                'result': 'success'
            }

    @pytest.mark.parametrize(
        'building',
        [1, 2, 3, 4, 5],
    )
    def test_up_building_max_level(self, building, default_user1):
        with create_session() as session:
            user1 = default_user1
            user1.money = 10000000
            user1.HQ_level = (
                user1.turret_level
            ) = user1.Miner1_level = user1.Miner2_level = user1.Wh_level = 5
            session.add(user1)
            session.commit()
            assert up_building(TierScheme(tier=building), default_user1.login) == {
                'result': 'max level reached'
            }

    def test_h_army_with_no_money(self, default_user1):
        with create_session() as session:
            user1 = default_user1
            session.add(user1)
            session.commit()
            assert h_army(TierScheme(tier=1), 100, user1.login) == {
                'result': 'not enough money'
            }

    def test_h_army_level_limit(self, default_user1):
        with create_session() as session:
            user1 = default_user1
            user1.money = 10000000
            session.add(user1)
            session.commit()
            assert h_army(TierScheme(tier=5), 100, user1.login) == {
                'result': 'HQ level is too low'
            }

    @pytest.mark.parametrize(
        'tier',
        [1, 2, 3, 4, 5],
    )
    def test_h_army_success(self, tier, default_user1):
        with create_session() as session:
            user1 = default_user1
            user1.money = 10000000
            user1.HQ_level = 5
            session.add(user1)
            session.commit()
            assert h_army(TierScheme(tier=tier), 1, user1.login) == {
                'result': 'hired successfully'
            }
