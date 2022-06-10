from http import HTTPStatus

import pytest
from flask import Flask

from app.datab import (
    Balances,
    Base,
    History,
    User,
    Values,
    create_engine,
    create_session,
    sessionmaker,
)
from app.views import (
    app,
    check_relevance,
    compare_lists,
    create_app,
    get_name_and_amount,
)

engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)


@pytest.fixture
def auth(client):
    return AuthActions(client)


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test'):
        return self._client.post('/login', data={'log_in': username})


@pytest.fixture(autouse=True)
def __init__db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_create_app():
    assert isinstance(create_app(), Flask)


def test_base(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK


def test_register(client):
    response = client.post('/register', data={'reg': 'testuser'})
    assert response.status_code == HTTPStatus.FOUND


def test_login(auth):
    assert auth.login().status_code == HTTPStatus.FOUND


def test_home(client, auth):
    with create_session() as session:
        u = User(id=1, name='test', money='1000')
        session.add(u)
    auth.login()
    response = client.get('/home')
    assert response.status_code == HTTPStatus.OK


def test_shop(client, auth):
    with create_session() as session:
        u = User(id=1, name='test', money='1000')
        session.add(u)
        v1 = Values(name='Alphacoin', value='100')
        v2 = Values(name='Betacoin', value='100')
        v3 = Values(name='Gammacoin', value='100')
        v4 = Values(name='Deltacoin', value='100')
        v5 = Values(name='Epsiloncoin', value='100')
        session.add(v1)
        session.add(v2)
        session.add(v3)
        session.add(v4)
        session.add(v5)
    auth.login()
    response = client.get('/home/shop')
    assert response.status_code == HTTPStatus.OK


def test_sell_page(client, auth):
    with create_session() as session:
        u = User(id=1, name='test', money='1000')
        session.add(u)
        v1 = Values(name='Alphacoin', value='100')
        v2 = Values(name='Betacoin', value='100')
        v3 = Values(name='Gammacoin', value='100')
        v4 = Values(name='Deltacoin', value='100')
        v5 = Values(name='Epsiloncoin', value='100')
        session.add(v1)
        session.add(v2)
        session.add(v3)
        session.add(v4)
        session.add(v5)
    auth.login()
    response = client.get('/home/sell')
    assert response.status_code == HTTPStatus.OK


def test_add(client, auth):
    with create_session() as session:
        u = User(id=1, name='test', money='1000')
        session.add(u)
        v1 = Values(name='Alphacoin', value='100')
        session.add(u)
        session.add(v1)
    auth.login()
    response1 = client.post('/add', data={'cur_adder': 'Omegacoin'})
    response2 = client.post('/add', data={'cur_adder': 'Alphacoin'})
    assert response1.status_code == HTTPStatus.FOUND
    assert response2.status_code == HTTPStatus.FOUND


def test_sell(client, auth):
    with create_session() as session:
        u = User(name='test', money='1000')
        v = Values(name='Alphacoin', value='100')
        b = Balances(username='test', cryptoname='Alphacoin', value='1')
        session.add(u)
        session.add(v)
        session.add(b)
    auth.login()
    client.post('/buy', data={'buy_crypto': 'Alphacoin 1'})
    response = client.post('/sell_1', data={'sell_crypto': 'Alphacoin: 1'})
    assert response.status_code == HTTPStatus.FOUND


def test_buy(client, auth):
    with create_session() as session:
        u = User(name='test', money='1000')
        session.add(u)
        v1 = Values(name='Alphacoin', value='100')
        v2 = Values(name='Betacoin', value='10000')
        session.add(v1)
        session.add(v2)
    auth.login()
    response1 = client.post('/buy', data={'buy_crypto': 'Alphacoin 1'})
    response2 = client.post('/buy', data={'buy_crypto': 'Betacoin 1'})
    assert response1.status_code == HTTPStatus.FOUND
    assert response2.status_code == HTTPStatus.FOUND


def test_compare_lists():
    assert (
        compare_lists(
            [
                Values(name='Alphacoin', value='100'),
                Values(name='Betacoin', value='100'),
            ],
            [
                Values(name='Alphacoin', value='101'),
                Values(name='Betacoin', value='101'),
            ],
        )
        is False
    )
    assert (
        compare_lists(
            [
                Values(name='Alphacoin', value='101'),
                Values(name='Betacoin', value='101'),
            ],
            [
                Values(name='Alphacoin', value='101'),
                Values(name='Betacoin', value='101'),
            ],
        )
        is True
    )


def test_check_relevance():
    with create_session() as session:
        v = Values(name='Alphacoin', value='101')
        v1 = Values(name='Betacoin', value='101')
        session.add(v)
        session.add(v1)
        value0 = [
            Values(name='Alphacoin', value='100'),
            Values(name='Betacoin', value='100'),
        ]
        assert check_relevance(value0, session, testing=True) is False
        value0 = [
            Values(name='Alphacoin', value='101'),
            Values(name='Betacoin', value='101'),
        ]
        assert check_relevance(value0, session, testing=True) is True


def test_get_name_and_amount():
    assert get_name_and_amount('Alphacoin 1') == ('Alphacoin', 1)


def test_user():
    u = User(id=1, name='abc', money='100')
    assert u.__repr__() == 'User abc'


def test_values():
    v = Values(id=1, name='abc', value='100')
    assert v.__repr__() == 'abc'


def test_history():
    h = History(id=1, id_of_user=1, action='buy', money='10', crypto='Alpha + 1')
    assert h.__repr__() == 'buy: 10 rubles, Alpha + 1'


def test_balances():
    b = Balances(id=1, username='abc', cryptoname='Alphacoin', value='100')
    assert b.__repr__() == 'Alphacoin: 100'
