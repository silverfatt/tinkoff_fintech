from statistics import mean
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import (
    Base,
    Film_d,
    Ratings_d,
    Reviews_d,
    User_d,
    create_session,
    engine,
)
from app.functions import makelist, paginate
from app.schemas import Film_s, User_s
from app.sort_keys import key_for_date_top, key_for_rating_top

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

Base.metadata.create_all(engine)


def user_authentificated(login: str, password: str) -> bool:
    with create_session() as session:
        q = session.query(User_d).filter_by(login=login).first()
        if q:
            res = check_password_hash(q.password, password)
            return res
        return False


@app.post('/token')
def login(
    data: OAuth2PasswordRequestForm = Depends(),
) -> Dict[str, Any]:  # pragma: no cover
    login = data.username
    password = data.password
    if user_authentificated(login, password):
        return {'access_token': login}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail='INCORRECT CREDENTIALS'
    )


@app.post('/register')
def register(new_user: User_s) -> Dict[str, str]:
    """
    register new user
    :param new_user: login and password
    :return: new user's credentials
    """
    with create_session() as session:
        q = session.query(User_d.id).filter(User_d.login == new_user.login)
        if session.query(q.exists()).scalar():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User already exists',
                headers={'WWW-Authenticate': 'Basic'},
            )
        hashed_password = generate_password_hash(str(new_user.password))
        u = User_d(login=new_user.login, password=hashed_password)
        session.add(u)
    return {'username': new_user.login, 'password': hashed_password}


@app.post('/add')
def add_new_film(
    film_to_add: Film_s, username: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """
    add new film to database
    :param film_to_add: title, director, date of release
    :param username: current user
    :return: status and username
    """
    with create_session() as session:
        film = session.query(Film_d).filter_by(title=film_to_add.title).first()
        if film:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='FILM ALREADY EXISTS'
            )
        film = Film_d(
            title=film_to_add.title,
            release=film_to_add.date_of_release,
            director=film_to_add.director,
            average_rating='0',
        )
        session.add(film)
        return {'user': username, 'status': 'ok'}


@app.post('/{title}/rate')
def rate_film(
    title: str, rating: int, username: str = Depends(oauth2_scheme)
) -> Dict[str, str]:  # pragma: no cover
    """
    sets/changes a user's rating to film
    :param title: film title
    :param rating: user's rating
    :param username: user's login
    :return: status and username
    """
    with create_session() as session:
        q = session.query(Film_d.id).filter(Film_d.title == title)
        if session.query(q.exists()).scalar():
            rq = (
                session.query(Ratings_d)
                .filter(Ratings_d.user == username)
                .filter(Ratings_d.title == title)
            )
            if session.query(rq.exists()).scalar():
                rq.one().rating = rating
                session.commit()
            else:
                r = Ratings_d(title=title, user=username, rating=rating)
                session.add(r)
            film = session.query(Film_d).filter(Film_d.title == title).one()
            r = session.query(Ratings_d).filter(Ratings_d.title == title).all()
            ratings = []
            for a in r:
                ratings.append(a.rating)
            if not isinstance(ratings, int):
                average = round(mean(ratings), 1)
            film.average_rating = str(average)
            session.commit()
    return {'status': 'ok', 'username': username}


@app.post('/{title}/review')
def review_film(
    title: str, review: str, username: str = Depends(oauth2_scheme)
) -> Dict[str, Any]:
    """
    sets/changes a user's review to film
    """
    with create_session() as session:
        film = session.query(Film_d).filter_by(title=title).first()
        if not film:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='FILM NOT FOUND'
            )
        reviewed = (
            session.query(Reviews_d).filter_by(title=title, user=username).first()
        )
        if reviewed:
            reviewed.review = review
            session.commit()
            return {'status': 'ok', 'username': username}
        review_in_history = Reviews_d(user=username, title=title, review=review)
        session.add(review_in_history)
        return {'status': 'ok'}


@app.post('/films/reviews/{title}')
def all_reviews(
    title: str,
    per_page: int = 5,
    page: int = 1,
    username: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    """
    shows all film's reviews
    """
    with create_session() as session:
        film = session.query(Film_d).filter_by(title=title).first()
        if not film:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='FILM NOT FOUND'
            )
        rq = session.query(Reviews_d).filter_by(title=title).all()
        reviews = []
        for r in rq:
            reviews.append(
                {
                    'film_title': r.title,
                    'username': r.user,
                    'review': r.review,
                }
            )
        return {
            'status': 'ok',
            'reviews': paginate(reviews, per_page, page),
            'username': username,
        }


@app.get('/films')
def show_all_films(
    films_per_page: int = 5,
    page: int = 1,
    username: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    """
    shows all films
    """
    with create_session() as session:
        q = session.query(Film_d).all()
        if not q:
            return {'status': 'ok', 'username': username}
        list_of_films = makelist(q)
        return {
            'status': 'ok',
            'data': paginate(list_of_films, films_per_page, page),
            'username': username,
        }


@app.get('/films/top/rating')
def top_of_films(
    per_page: int = 10, page: int = 1, username: str = Depends(oauth2_scheme)
) -> Dict[str, Any]:
    """
    shows films sorted by rating
    """
    with create_session() as session:
        q = session.query(Film_d).all()
        if not q:
            return {'status': 'ok', 'username': username}
        list_of_films = makelist(sorted(q, key=key_for_rating_top, reverse=True))
        return {
            'status': 'ok',
            'data': paginate(list_of_films, per_page, page),
            'username': username,
        }


@app.get('/films/top/date')
def films_top_date(
    per_page: int = 10, page: int = 1, username: str = Depends(oauth2_scheme)
) -> Dict[str, Any]:
    """
    shows films sorted by date
    """
    with create_session() as session:
        q = session.query(Film_d).all()
        if not q:
            return {'status': 'ok', 'username': username}
        list_of_films = makelist(sorted(q, key=key_for_date_top, reverse=True))
        return {
            'status': 'ok',
            'data': paginate(list_of_films, per_page, page),
            'username': username,
        }


@app.get('/films/search_{substring}')
def substring_search(
    substring: str,
    per_page: int = 10,
    page: int = 1,
    username: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    """
    search films with a substring
    """
    with create_session() as session:
        q = session.query(Film_d).filter(Film_d.title.contains(substring)).all()
        if not q:
            return {'status': 'ok', 'username': username}
        list_of_films = makelist(q)
        return {
            'status': 'ok',
            'data': paginate(list_of_films, per_page, page),
            'username': username,
        }


@app.get('/about/{title}')
def about_film(title: str, username: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    show's all information about film
    """
    with create_session() as session:
        q = session.query(Film_d).filter_by(title=title).first()
        if not q:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='FILM NOT FOUND'
            )
        return {
            'status': 'ok',
            'username': username,
            'title': title,
            'date_of_release': q.release,
            'rating': q.average_rating,
        }
