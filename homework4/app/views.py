from decimal import Decimal
from typing import List

import werkzeug.wrappers.response
from flask import Flask, flash, redirect, render_template, request, url_for

from app.config import SECRET_KEY
from app.datab import Balances, History, Session, User, Values, create_session
from app.functions import compare_lists, get_name_and_amount, paginate

user_name = 'user'
value0 = None  # type = User
value1 = None  # type = User


def create_app() -> Flask:
    """
    Creates app
    :return: app
    """
    myapp = Flask(__name__)
    myapp.secret_key = SECRET_KEY
    return myapp


app = create_app()


@app.route('/', methods=['GET', 'POST'])
def base() -> str:
    """
    Renders start page
    :return: str
    """
    site = render_template('auth.html')
    return site


@app.route('/home')
def home_page() -> str:
    """
    Renders home page
    :return:
    """

    with create_session() as session:
        u = session.query(User).filter(User.name == user_name).one()
        q = session.query(Balances).filter(Balances.username == user_name).all()
        m = session.query(User).filter(User.name == user_name).one().money
        h = session.query(History).filter(History.id_of_user == u.id).all()
        number_of_posts = 5
        page = request.args.get('number')
        allPosts, prev, next_ = paginate(number_of_posts, page, h)  # type: ignore
        session.expunge_all()
    site = render_template(
        'home.html',
        username=user_name,
        money=m,
        crypto_list=q,
        operations=allPosts,
        prev=prev,
        next=next_,
    )
    return site


@app.route('/login', methods=['POST'])
def login_page() -> werkzeug.wrappers.response.Response:
    """
    Checks if user is in db and sends him to main page if he is
    :return: str
    """
    global user_name
    login = request.form.get('log_in')
    with create_session() as session:
        q = session.query(User.id).filter(User.name == login)
        if session.query(q.exists()).scalar():
            user_name = str(login)
            return redirect(url_for('home_page'))
        flash("User doesn't exist!")
        return redirect(url_for('base'))


@app.route('/register', methods=['POST'])
def register_page() -> werkzeug.wrappers.response.Response:
    """
    Adds new user
    :return:
    """
    global user_name
    login = request.form.get('reg')
    with create_session() as session:
        q = session.query(User.id).filter(User.name == login)
        if session.query(q.exists()).scalar():
            flash('User already exists!')
            return redirect(url_for('base'))
        u = User(name=login, money='1000')
        session.add(u)
        session.flush()
        h = History(id_of_user=u.id, action='register', money='+1000', crypto='+0')
        session.add(h)
        session.flush()
        # for value in values:
        #     b = Balances(username=login, cryptoname=value.name, value='0')
        #     session.add(b)
        user_name = str(login)
        return redirect(url_for('home_page'))


@app.route('/add', methods=['GET', 'POST'])
def add_currency() -> werkzeug.wrappers.response.Response:
    """
    adds new currency
    :return:
    """
    currency = request.form.get('cur_adder')
    if str(currency).isspace() or currency == '':
        flash('Incorrect name (probably it is empty)')
        return redirect(url_for('home_page'))
    with create_session() as session:
        currency = str(currency).strip()
        q = session.query(Values.name).filter(Values.name == currency)
        if not session.query(q.exists()).scalar():
            v = Values(name=currency, value='100')
            b = Balances(username=user_name, cryptoname=currency, value='1')
            session.add(v)
            session.add(b)
            session.flush()
            session.expunge_all()
        else:
            flash('Already exists!')
    return redirect(url_for('home_page'))


@app.route('/home/shop')
def shop_page() -> str:
    """
    renders shop page
    :return:
    """
    global value0
    with create_session() as session:
        q = session.query(Values).all()
        u = session.query(User).filter(User.name == user_name).one()
        value0 = q.copy()
        session.expunge_all()
    site = render_template('shop.html', crypto_values=q, crypto_prices=q, money=u.money)
    return site


def check_relevance(
    values: List[Values], session: Session, testing: bool = False
) -> bool:
    """
    checks if price is relevant
    :param values: price that is being shown
    :param session: database session
    :param testing: where the function is being called - True if in tests
    :return:
    """
    flag = True
    q = session.query(Values).all()
    if not compare_lists(q, values):  # type: ignore
        flag = False
        if not testing:
            flash('Operation failed: currency value in unrelevant')
    return flag


@app.route('/buy', methods=['GET', 'POST'])
def buy_crypto() -> werkzeug.wrappers.response.Response:
    """
    makes all changes in database after buying a crypto
    :return:
    """
    with create_session() as session:
        flag = check_relevance(value0, session)  # type: ignore
    if flag:
        crypto_to_buy = request.form.get('buy_crypto')
        crypto, amount = get_name_and_amount(str(crypto_to_buy))
        with create_session() as session:
            requested_crypto = session.query(Values).filter(Values.name == crypto).one()
            user = session.query(User).filter(User.name == user_name).one()
            if Decimal(user.money) >= Decimal(
                str(Decimal(requested_crypto.value) * amount)
            ):
                flash('Successfully bought!')
                h = History(
                    id_of_user=user.id,
                    action='buy',
                    money=f'-{str(Decimal(requested_crypto.value) * amount)}',
                    crypto=f'+{amount} {crypto}',
                )
                session.add(h)
                session.flush()
                q = (
                    session.query(Balances)
                    .filter(Balances.cryptoname == crypto)
                    .filter(Balances.username == user.name)
                )
                if not session.query(q.exists()).scalar():
                    b = Balances(username=user_name, cryptoname=crypto, value='0')
                    session.add(b)
                q = (
                    session.query(Balances)
                    .filter(Balances.cryptoname == crypto)
                    .filter(Balances.username == user.name)
                    .one()
                )
                q.value = str(int(q.value) + amount)
                user.money = str(
                    Decimal(user.money) - Decimal(requested_crypto.value) * amount
                )
                session.commit()
            else:
                flash('Not enougth money!')
    return redirect(url_for('shop_page'))


@app.route('/home/sell', methods=['GET', 'POST'])
def sell_page() -> str:
    """
    renders sell page
    :return:
    """
    global value1
    with create_session() as session:
        q = (
            session.query(Balances)
            .filter(Balances.username == user_name)
            .filter(Balances.value != '0')
            .all()
        )
        v = session.query(Values).all()
        u = session.query(User).filter(User.name == user_name).one()
        value1 = v.copy()
        session.expunge_all()
    site = render_template('sell.html', crypto_list=q, crypto_values=v, money=u.money)
    return site


@app.route('/sell_1', methods=['GET', 'POST'])
def sell_crypto() -> werkzeug.wrappers.response.Response:
    """
    makes all changes in database after selling a crypto
    :return:
    """
    with create_session() as session:
        flag = check_relevance(value1, session)  # type: ignore
    if flag:
        flash('Successfully sold!')
        crypto_to_sell = request.form.get('sell_crypto')
        crypto = get_name_and_amount(str(crypto_to_sell))[0]
        crypto = crypto[0 : len(crypto) - 1]
        with create_session() as session:
            q = (
                session.query(Balances)
                .filter(Balances.username == user_name)
                .filter(Balances.cryptoname == crypto)
                .one()
            )
            v = session.query(Values).filter(Values.name == crypto).one()
            q.value = str(int(q.value) - 1)
            user = session.query(User).filter(User.name == user_name).one()
            h = History(
                id_of_user=user.id,
                action='sell',
                money=f'+{v.value}',
                crypto=f'-1 {crypto}',
            )
            session.add(h)
            session.flush()
            user.money = str(Decimal(user.money) + Decimal(v.value))
            session.commit()
    return redirect(url_for('sell_page'))
