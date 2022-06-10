import pytest

from app.database import create_session
from app.guild import send_reinforcements_to_ally


class TestSendReinforcementsToAlly:
    def test_send_reinforcements_to_myself(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert send_reinforcements_to_ally(
                1, 5, default_user1.login, default_user1.login
            ) == {'error': 'you cannot trade with yourself!'}

    def test_send_reinforcements_no_user_exist(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert send_reinforcements_to_ally(1, 5, 'wfq', default_user1.login) == {
                'error': 'user does not exist'
            }

    def test_send_reinforcements_not_a_guild_member(self, default_user1, default_user2):
        with create_session() as session:
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert send_reinforcements_to_ally(
                1, 5, default_user2.login, default_user1.login
            ) == {'error': 'you are not a member of any guild'}

    def test_send_reinforcements_to_not_a_guild_member(
        self, default_user1, default_user2, default_guild
    ):
        with create_session() as session:
            default_user1.guild = default_guild.name
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert send_reinforcements_to_ally(
                1, 5, default_user2.login, default_user1.login
            ) == {'error': 'user is not a member of your guild'}

    @pytest.mark.parametrize(
        'tier',
        [1, 2, 3, 4, 5],
    )
    def test_send_reinforcements_not_enough_soldiers(
        self, tier, default_user1, default_user2, default_guild
    ):
        with create_session() as session:
            default_user1.guild = default_guild.name
            default_user2.guild = default_guild.name
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert send_reinforcements_to_ally(
                tier, 100, default_user2.login, default_user1.login
            ) == {'error': 'not enough soldiers'}

    @pytest.mark.parametrize(
        'tier',
        [1, 2, 3, 4, 5],
    )
    def test_send_reinforcements_success(
        self, tier, default_user1, default_user2, default_guild
    ):
        with create_session() as session:
            default_user1.soldiers_t1 = 1
            default_user1.soldiers_t2 = 1
            default_user1.soldiers_t3 = 1
            default_user1.soldiers_t4 = 1
            default_user1.soldiers_t5 = 1
            default_user1.guild = default_guild.name
            default_user2.guild = default_guild.name
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert send_reinforcements_to_ally(
                tier, 1, default_user2.login, default_user1.login
            ) == {'result': 'success'}
