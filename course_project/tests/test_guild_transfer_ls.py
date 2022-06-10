from app.database import create_session
from app.guild import transfer_leadership


class TestTransferLeadership:
    def test_transfer_leadership_myself(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert transfer_leadership(default_user1.login, default_user1.login) == {
                'error': 'you cannot transfer leadership to yourself'
            }

    def test_transfer_no_user_exist(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert transfer_leadership('wfq', default_user1.login) == {
                'error': 'no such player'
            }

    def test_transfer_not_a_guild_member(self, default_user1, default_user2):
        with create_session() as session:
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert transfer_leadership(default_user2.login, default_user1.login) == {
                'error': 'you are not a member of any guild'
            }

    def test_transfer_to_not_a_guild_member(
        self, default_user1, default_user2, default_guild
    ):
        with create_session() as session:
            default_user1.guild = default_guild.name
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert transfer_leadership(default_user2.login, default_user1.login) == {
                'error': 'user is not a member of your guild'
            }

    def test_transfer_success(self, default_user1, default_user2, default_guild):
        with create_session() as session:
            default_user1.guild = default_guild.name
            default_user2.guild = default_guild.name
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert transfer_leadership(default_user2.login, default_user1.login) == {
                'result': 'success'
            }
