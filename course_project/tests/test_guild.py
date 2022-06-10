from app.database import create_session
from app.guild import (
    add_note_to_board,
    c_guild,
    j_guild,
    kick,
    leave,
    send_res,
    show_all_notes,
    show_guilds,
    show_my_guild,
)


class TestCreateAndJoin:
    def test_c_guild_exists(self, default_guild, default_user1):
        with create_session() as session:
            session.add(default_guild)
            session.add(default_user1)
            session.commit()
            assert c_guild(default_guild.name, default_user1.login) == {
                'error': 'already exists'
            }

    def test_c_guild_already_member(self, default_user1):
        with create_session() as session:
            user = default_user1
            user.guild = 'default'
            session.add(default_user1)
            session.commit()
            assert c_guild('fqwfq', default_user1.login) == {
                'error': 'you are already a member of guild'
            }

    def test_c_guild_no_money(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert c_guild('fqwfq', default_user1.login) == {
                'error': 'not enough money'
            }

    def test_c_guild_success(self, default_user1):
        with create_session() as session:
            user = default_user1
            user.money = 1000
            session.add(default_user1)
            session.commit()
            assert c_guild('fqwfq', default_user1.login) == {
                'result': 'guild fqwfq succesfully created!'
            }

    def test_j_guild_does_not_exist(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert j_guild('wqfq', default_user1.login) == {
                'error': 'guild does not exist'
            }

    def test_j_guild_success(self, default_guild, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.add(default_guild)
            session.commit()
            assert j_guild(default_guild.name, default_user1.login) == {
                'result': 'wellcome to default!'
            }


class TestShowMyGuild:
    def test_show_my_guild_not_a_member(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert show_my_guild(default_user1.login) == {
                'error': 'you are not a member of a guild'
            }

    def test_show_my_guild_success(self, default_user1, default_guild):
        with create_session() as session:
            user = default_user1
            user.guild = default_guild.name
            session.add(default_guild)
            session.add(user)
            session.commit()
            assert show_my_guild(default_user1.login) == {
                'User1': 'HQ level: 1 rank: member'
            }


class TestSendRes:
    def test_send_res_to_myself(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert send_res(0, 0, default_user1.login, default_user1.login) == {
                'error': 'you cannot trade with yourself!'
            }

    def test_send_res_no_guild(self, default_user1, default_user2):
        with create_session() as session:
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert send_res(0, 0, default_user2.login, default_user1.login) == {
                'error': 'you are not a member of any guild'
            }

    def test_send_res_no_member(self, default_user1, default_user2, default_guild):
        with create_session() as session:
            default_user1.guild = default_guild.name
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert send_res(0, 0, default_user2.login, default_user1.login) == {
                'error': 'user is not a member of your guild'
            }

    def test_send_res_no_user_exist(self, default_user1, default_user2, default_guild):
        with create_session() as session:
            default_user1.guild = default_guild.name
            session.add(default_user1)
            session.commit()
            assert send_res(0, 0, default_user2.login, default_user1.login) == {
                'error': 'user does not exist'
            }

    def test_send_res_not_enough_resourses(
        self, default_user1, default_user2, default_guild
    ):
        with create_session() as session:
            default_user1.guild = default_guild.name
            default_user2.guild = default_guild.name
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert send_res(1000, 1000, default_user2.login, default_user1.login) == {
                'error': "you don't have enough resourses"
            }

    def test_send_res_not_enough_space(
        self, default_user1, default_user2, default_guild
    ):
        with create_session() as session:
            default_user1.guild = default_guild.name
            default_user1.Wh_level = 5
            default_user1.money = 2000
            default_user1.food = 2000
            default_user2.guild = default_guild.name
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert send_res(1500, 1500, default_user2.login, default_user1.login) == {
                'error': 'reciever has not enough space in warehouse'
            }

    def test_send_res_success(self, default_user1, default_user2, default_guild):
        with create_session() as session:
            default_user1.guild = default_guild.name
            default_user1.money = 1000
            default_user1.food = 1000
            default_user2.guild = default_guild.name
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert send_res(100, 100, default_user2.login, default_user1.login) == {
                'result': 'success'
            }


class TestKick:
    def test_kick_myself(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert kick(default_user1.login, default_user1.login) == {
                'error': 'you cannot kick yourself!'
            }

    def test_kick_no_user_exist(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert kick('qwfq', default_user1.login) == {'error': 'user does not exist'}

    def test_kick_no_guild(self, default_user1, default_user2):
        with create_session() as session:
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert kick(default_user2.login, default_user1.login) == {
                'error': 'you are not a member of any guild'
            }

    def test_kick_not_a_member(self, default_user1, default_user2, default_guild):
        with create_session() as session:
            default_user1.guild = default_guild.name
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert kick(default_user2.login, default_user1.login) == {
                'error': 'user is not a member of your guild'
            }

    def test_kick_not_a_leader(self, default_user1, default_user2, default_guild):
        with create_session() as session:
            default_user1.guild = default_guild.name
            default_user2.guild = default_guild.name
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert kick(default_user2.login, default_user1.login) == {
                'error': 'only leader can kick players'
            }

    def test_kick_success(self, default_user1, default_user2, default_guild):
        with create_session() as session:
            default_user1.guild = default_guild.name
            default_user2.guild = default_guild.name
            default_user1.rank = 'leader'
            session.add(default_user1)
            session.add(default_user2)
            session.commit()
            assert kick(default_user2.login, default_user1.login) == {
                'result': 'success'
            }


class TestLeave:
    def test_leave_no_guild(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert leave(default_user1.login) == {
                'error': 'you are not a member of any guild'
            }

    def test_leave_member(self, default_user1, default_guild):
        with create_session() as session:
            default_user1.guild = default_guild.name
            session.add(default_user1)
            session.commit()
            assert leave(default_user1.login) == {'result': 'successfully left'}

    def test_leave_leader(self, default_user1, default_guild):
        with create_session() as session:
            default_user1.guild = default_guild.name
            default_user1.rank = 'leader'
            session.add(default_user1)
            session.add(default_guild)
            session.commit()
            assert leave(default_user1.login) == {'result': 'success'}


class TestShowGuilds:
    def test_show_guilds_no_guilds(self):
        assert show_guilds() == {'guilds': []}

    def test_show_guilds_success(self, default_guild):
        with create_session() as session:
            session.add(default_guild)
            session.commit()
            assert show_guilds() == {'guilds': ['default']}


class TestNotes:
    def test_add_note_to_board_not_a_member(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert add_note_to_board('fwqfq', default_user1.login) == {
                'error': 'you are not a member of a guild'
            }

    def test_add_note_to_board_success(self, default_user1, default_guild):
        with create_session() as session:
            default_user1.guild = default_guild.name
            session.add(default_user1)
            session.commit()
            assert add_note_to_board('wavqacfq', default_user1.login) == {
                'result': 'success'
            }

    def test_show_all_notes_not_a_member(self, default_user1):
        with create_session() as session:
            session.add(default_user1)
            session.commit()
            assert show_all_notes(default_user1.login) == {
                'error': 'you are not a member of a guild'
            }

    def test_show_all_notes_success(self, default_user1, default_guild):
        with create_session() as session:
            default_user1.guild = default_guild.name
            session.add(default_user1)
            session.commit()
            add_note_to_board('text', default_user1.login)
            assert show_all_notes(default_user1.login) == {'default': ['User1:  text']}
