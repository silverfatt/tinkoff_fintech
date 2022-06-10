import pytest

from app.new_user import make_bot, make_new_user


class TestNewUser:
    def test_make_new_user(self, default_user1):
        user = default_user1
        new_user = make_new_user('User1', '123')
        assert new_user.login == user.login and new_user.password == user.password

    @pytest.mark.parametrize(
        'level, amounts',
        [
            (1, (5, 4, 3, 2, 1)),
            (2, (10, 8, 6, 4, 2)),
            (3, (15, 12, 9, 6, 3)),
            (4, (20, 16, 12, 8, 4)),
            (5, (25, 20, 15, 10, 5)),
        ],
    )
    def test_make_bot(self, level, amounts):
        bot = make_bot(level)
        assert (
            bot.soldiers_t1,
            bot.soldiers_t2,
            bot.soldiers_t3,
            bot.soldiers_t4,
            bot.soldiers_t5,
        ) == amounts
