import pytest
from fastapi import HTTPException

from app.schemas import Amount, Message, Name, TierScheme, UserScheme


class TestUserSS:
    @pytest.mark.parametrize(
        'login,password',
        [('', ''), ('a' * 30, ''), ('GoodLogin', ''), ('GoodLogin', 'a' * 40)],
    )
    def test_user_s_validators_incorrect(self, login, password):
        with pytest.raises(HTTPException):
            UserScheme(login=login, password=password)

    def test_user_s_validators_correct(self):
        user = UserScheme(login='GoodLogin', password='GoodPassword')
        assert user.check_name(value=user.login) == 'GoodLogin'
        assert user.check_password(value=user.password) == 'GoodPassword'


class TestTierValidator:
    @pytest.mark.parametrize(
        'level',
        [0, 6],
    )
    def test_tier_validators_incorrect(self, level):
        with pytest.raises(HTTPException):
            TierScheme(tier=level)

    def test_tier_validators_correct(self):
        user = TierScheme(tier=3)
        assert user.check_number(value=user.tier) == 3


class TestName:
    @pytest.mark.parametrize(
        'name',
        ['', '   ', 'a' * 51],
    )
    def test_name_validators_incorrect(self, name):
        with pytest.raises(HTTPException):
            Name(name=name)

    def test_name_validators_correct(self):
        name = Name(name='GoodName')
        assert name.check_name(name='GoodName') == 'GoodName'


class TestMessage:
    @pytest.mark.parametrize(
        'message',
        ['', '     '],
    )
    def test_message_validators_incorrect(self, message):
        with pytest.raises(HTTPException):
            Message(text=message)

    def test_message_validators_correct(self):
        message = Message(text='GoodText')
        assert message.check_name(text='GoodText') == 'GoodText'


class TestAmount:
    @pytest.mark.parametrize(
        'amount',
        [-1, 0],
    )
    def test_amount_validators_incorrect(self, amount):
        with pytest.raises(HTTPException):
            Amount(amount=amount)

    def test_amount_validators_correct(self):
        message = Amount(amount=5)
        assert message.check_name(amount=5) == 5
