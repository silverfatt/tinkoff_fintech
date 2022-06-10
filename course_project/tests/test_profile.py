from app.database import FightHistory, create_session
from app.profile import get_economy_information, get_fight_h, get_profile_info


class TestProfile:
    def test_get_profile_info(self, default_user1):
        with create_session() as session:
            user1 = default_user1
            session.add(user1)
            session.commit()
            assert get_profile_info(user1.login) == user1.get_user_info()

    def test_get_economy_info(self, default_user1):
        with create_session() as session:
            user1 = default_user1
            session.add(user1)
            session.commit()
            assert get_economy_information(user1.login) == {
                'money': 0,
                'food': 0,
                'money income': 150,
                'food summary income': 140,
                'food income': 150,
                'food outcome (from soldiers)': 10,
            }

    def test_get_fight_h(self, default_user1):
        with create_session() as session:
            user1 = default_user1
            fight_history = FightHistory(
                event='attack', player1='User1', player2='User2', result='draw'
            )
            session.add(fight_history)
            session.add(user1)
            session.commit()
            assert get_fight_h(user1.login) == {'attack': 'User1 vs User2, draw'}
