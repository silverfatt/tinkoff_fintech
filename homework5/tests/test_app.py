import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from werkzeug.security import generate_password_hash

from app.database import (
    Base,
    Film_d,
    User_d,
    create_engine,
    create_session,
    sessionmaker,
)
from app.functions import makelist
from app.main import app, user_authentificated
from app.schemas import Film_s, User_s
from app.sort_keys import key_for_date_top, key_for_rating_top

engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)
client = TestClient(app)

with create_session() as session:
    q = session.query(Film_d.id).filter(Film_d.title == 'The Matrix')
    if not session.query(q.exists()).scalar():
        f1 = Film_d(
            title='The Matrix', director='Vachovski', release=1999, average_rating='0'
        )
        flist = [f1]
        for f in flist:
            session.add(f)


@pytest.fixture(autouse=True)
def __init__db():
    Base.metadata.create_all(engine)
    yield
    # Base.metadata.drop_all(engine)


@pytest.fixture
def film1():
    f = Film_d(
        title='The Matrix', director='Vachovski', release=1999, average_rating='6'
    )
    return f


@pytest.fixture
def film2():
    f = Film_d(title='Iron Man', director='Favro', release=2008, average_rating='8')
    return f


def test_key_for_date_top(film1):
    assert key_for_date_top(film1) == 1999


def test_key_for_rating_top(film1):
    assert key_for_rating_top(film1) == '6'


def test_makelist(film1, film2):
    list_of_films = [film1, film2]
    reslist = [
        {
            'title': 'The Matrix',
            'director': 'Vachovski',
            'release': 1999,
            'average_rating': '6',
        },
        {
            'title': 'Iron Man',
            'director': 'Favro',
            'release': 2008,
            'average_rating': '8',
        },
    ]
    assert makelist(list_of_films) == reslist


@pytest.mark.parametrize(
    'login,password',
    [('', ''), ('a' * 30, ''), ('GoodLogin', ''), ('GoodLogin', 'a' * 40)],
)
def test_user_s_validators_requests(login, password):
    with pytest.raises(HTTPException):
        User_s(login=login, password=password)


def test_user_s_validators_return():
    u = User_s(login='GoodLogin', password='GoodPassword')
    assert u.check_name(u.login) == 'GoodLogin'
    assert u.check_password(u.password) == 'GoodPassword'


@pytest.mark.parametrize(
    'title,date,director',
    [
        ('', 1, ''),
        ('a' * 50, 1, ''),
        ('GoodTitle', 1, ''),
        ('GoodTitle', 10000, ''),
        ('GoodTitle', None, ''),
        ('GoodTitle', 1999, ''),
        ('GoodTitle', 1999, 'a' * 50),
    ],
)
def test_film_s_validators_requests(title, date, director):
    with pytest.raises(HTTPException):
        Film_s(title=title, date_of_release=date, director=director)


def test_film_s_validators_return():
    f = Film_s(title='GoodTitle', date_of_release=1999, director='GoodDirector')
    assert f.check_title(f.title) == 'GoodTitle'
    assert f.check_date(f.date_of_release) == 1999
    assert f.check_director(f.director) == 'GoodDirector'


def test_register():
    with create_session() as session:
        u = User_d(login='Existing', password='sqfwfcca')
        session.add(u)
    u_s = User_s(login='Existing', password='afdqwsfc')
    msg = {'login': u_s.login, 'password': u_s.password}
    response = client.post('/register', json=msg)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    u_s = User_s(login='NotExisting', password='afdqwsfc')
    msg = {'login': u_s.login, 'password': u_s.password}
    response = client.post('/register', json=msg)
    assert response.status_code == status.HTTP_200_OK


def test_add_film(film1):
    f1 = film1
    msg = {'title': f1.title, 'date_of_release': f1.release, 'director': f1.director}
    response = client.post('/add', json=msg, headers={'Authorization': 'Bearer login'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    msg = {
        'title': 'The Matrix 4!',
        'date_of_release': f1.release,
        'director': f1.director,
    }
    response = client.post('/add', json=msg, headers={'Authorization': 'Bearer login'})
    assert response.status_code == status.HTTP_200_OK


def test_show_all_films(film1):
    with create_session() as session:
        f = film1
        session.add(f)
        session.expunge_all()
    msg = {'films_per_page': 5, 'page': 1}
    response = client.get('/films', json=msg, headers={'Authorization': 'Bearer login'})
    assert response.status_code == status.HTTP_200_OK


def test_rate_film(film1):
    with create_session() as session:
        f1 = film1
        session.add(f1)
        session.expunge_all()
    msg = {'title': f1.title, 'rating': 5}
    response = client.post(
        'The%20Matrix/rate?rating=5', msg, headers={'Authorization': 'Bearer login'}
    )
    assert response.status_code == status.HTTP_200_OK


def test_review_film(film1):
    with create_session() as session:
        f1 = film1
        session.add(f1)
        session.expunge_all()
    msg = {'title': f1.title, 'review': 'text'}
    response = client.post(
        'The%20Matrix/review?review=text',
        msg,
        headers={'Authorization': 'Bearer login'},
    )
    assert response.status_code == status.HTTP_200_OK


def test_all_reviews():
    with create_session() as session:
        f1 = Film_d(
            title='The Matrix', director='Vachovski', release=1999, average_rating='6'
        )
        session.add(f1)
        session.expunge_all()
    msg = {'title': f1.title, 'per_page': 5, 'page': 1}
    print(f1.title)
    response = client.post(
        f'/films/reviews/{f1.title}', msg, headers={'Authorization': 'Bearer login'}
    )
    print(response.json())
    assert response.status_code == status.HTTP_200_OK


def test_top_of_films(film1):
    with create_session() as session:
        f = film1
        session.add(f)
        session.expunge_all()
    msg = {'films_per_page': 5, 'page': 1}
    response = client.get(
        '/films/top/rating', json=msg, headers={'Authorization': 'Bearer login'}
    )
    assert response.status_code == status.HTTP_200_OK


def test_films_top_date(film1):
    with create_session() as session:
        f = film1
        session.add(f)
        session.expunge_all()
    msg = {'films_per_page': 5, 'page': 1}
    response = client.get(
        '/films/top/date', json=msg, headers={'Authorization': 'Bearer login'}
    )
    assert response.status_code == status.HTTP_200_OK


def test_substrung_search(film1):
    with create_session() as session:
        f = film1
        session.add(f)
        session.expunge_all()
    msg = {
        'substring': 'm',
        'per_page': 5,
        'page': 1,
    }
    response = client.get(
        '/films/search_m?per_page=5&page=1',
        json=msg,
        headers={'Authorization': 'Bearer login'},
    )
    assert response.status_code == status.HTTP_200_OK


def test_about_film():
    f = Film_d(
        title='The Matrix', director='Vachovski', release=1999, average_rating='0'
    )
    with create_session() as session:
        session.add(f)
        msg = {'title': f.title}
        session.expunge_all()
    response = client.get(
        f'/about/{f.title}', json=msg, headers={'Authorization': 'Bearer login'}
    )
    assert response.status_code == status.HTTP_200_OK


def test_user_authentificated():
    with create_session() as session:
        u = User_d(login='Existing', password=generate_password_hash('sqfwfcca'))
        session.add(u)
        session.expunge_all()
    assert user_authentificated(u.login, 'sqfwfcca') is False
