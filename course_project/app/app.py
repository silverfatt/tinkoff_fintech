from threading import Thread
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from werkzeug.security import check_password_hash, generate_password_hash

from app.build_and_hire import h_army, up_building
from app.database import Base, User, create_session, engine, prepare_db
from app.fight import attack, attack_b
from app.guild import (
    add_note_to_board,
    c_guild,
    j_guild,
    kick,
    leave,
    send_reinforcements_to_ally,
    send_res,
    show_all_notes,
    show_guilds,
    show_my_guild,
    transfer_leadership,
)
from app.new_user import make_new_user
from app.profile import get_economy_information, get_fight_h, get_profile_info
from app.schemas import Amount, Message, Name, TierScheme, UserScheme
from app.thread_func import run_background_calculations

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

Base.metadata.create_all(engine)
prepare_db()

th = Thread(target=run_background_calculations)
th.daemon = True
th.start()


def user_authenticated(login: str, password: str) -> bool:
    with create_session() as session:  # pragma: no cover
        user_query = session.query(User).filter_by(login=login).first()
        if user_query:
            return check_password_hash(user_query.password, password)
        return False


@app.post('/token')
async def authenticate(
    data: OAuth2PasswordRequestForm = Depends(),
) -> Dict[str, Any]:  # pragma: no cover
    login = data.username
    password = data.password
    if user_authenticated(login, password):
        return {'access_token': login}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail='INCORRECT CREDENTIALS'
    )


@app.post('/register')
async def register(new_user: UserScheme) -> Dict[str, str]:
    """
    Register new user
    """
    with create_session() as session:
        user_query = session.query(User.id).filter(User.login == new_user.login)
        if session.query(user_query.exists()).scalar():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User already exists',
                headers={'WWW-Authenticate': 'Basic'},
            )
        hashed_password = generate_password_hash(str(new_user.password))
        user = make_new_user(new_user.login, hashed_password)
        session.add(user)
    return {'username': new_user.login, 'password': hashed_password}


@app.get('/profile')
async def get_user_information(
    username: str = Depends(oauth2_scheme),
) -> Dict[str, str]:
    """
    Get information about user - power, buildings, etc.
    """
    return get_profile_info(username)


@app.get('/profile/economy')
async def get_economy_info(
    username: str = Depends(oauth2_scheme),
) -> Dict[str, str]:
    """
    Get more detailed information about money and food incomes
    """
    return get_economy_information(username)


@app.get('/profile/history')
async def get_fight_history(username: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """
    Get history of fights
    """
    return get_fight_h(username)


@app.get('/users')
async def search_for_enemies(username: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """
    Get list of players and their HQ's
    """
    with create_session() as session:
        users = session.query(User).all()
        users_dictionary = {
            user.login: f'HQ level: {str(user.HQ_level)} rating: {str(user.rating)}'
            for user in users
        }
        return users_dictionary


@app.post('/attack')
async def attack_other_user(
    user_to_attack: Name, username: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """
    Attack other player to gather resources and rating
    """
    return attack(user_to_attack.name, username)


@app.post('/attack_bot')
async def attack_bot(
    level: TierScheme, username: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """
    Don't have enough rating? Get it by attacking bots!
    Higher level - more resources!
    Amount of soldiers (T1, T2, T3, T4, T5) and for each level
    ||1:  5, 4, 3, 2, 1||
    ||2:  10, 8, 6, 4, 2||
    ||3:  15, 12, 9, 6, 3||
    ||4:  20, 16, 12, 8, 4||
    ||5:  25, 20, 15, 10, 5||
    """
    return attack_b(username, level.tier)


@app.post('/upgrade_building')
async def upgrade_building(
    building_form: TierScheme, username: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """
    Upgrade building. 1 - HQ, 2 - MoneyMiner, 3 - FoodMiner, 4 - Warehouse, 5 - Turret
    """
    return up_building(building_form, username)


@app.post('/hire_army')
async def hire_army(
    hiring_form: TierScheme,
    amount: Amount,
    username: str = Depends(oauth2_scheme),
) -> Dict[str, str]:
    """
    1 - Tier 1, 2 - Tier 2, ..., 5 - Tier 5
    """
    return h_army(hiring_form, amount.amount, username)


@app.post('/create_guild')
async def create_guild(
    guild_name: Name, username: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """
    Create new guild. Costs 1000 money!
    """
    return c_guild(guild_name.name, username)


@app.post('/join_guild')
async def join_guild(
    guild_name: Name, username: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """
    Join an existing guild
    """
    return j_guild(guild_name.name, username)


@app.get('/my_guild')
async def my_guild(username: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """
    Check members of your guild
    """
    return show_my_guild(username)


@app.post('/my_guild/trade')
async def send_resourses(
    money: Amount, food: Amount, send_to: Name, username: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """
    Send resourses to your guild's member
    """
    return send_res(money.amount, food.amount, send_to.name, username)


@app.post('/my_guild/reinforce')
async def send_reinforcements(
    tier: TierScheme,
    amount: Amount,
    send_to: Name,
    username: str = Depends(oauth2_scheme),
) -> Dict[str, str]:
    """
    Send soldiers to your guild's member
    """
    return send_reinforcements_to_ally(tier.tier, amount.amount, send_to.name, username)


@app.post('/my_guild/kick')
async def kick_from_guild(
    member_to_kick: Name, username: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """
    Kick a member of your guild
    """
    return kick(member_to_kick.name, username)


@app.post('/my_guild/leave')
async def leave_guild(username: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """
    Leave a guild. If you are a leader, guild will be disbanded
    """
    return leave(username)


@app.post('/my_guild/make_leader')
async def make_leader(
    new_leader: Name, username: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """
    Make other player a new leader of your guild
    """
    return transfer_leadership(new_leader.name, username)


@app.post('/my_guild/add_note')
async def add_note(
    message: Message, username: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """
    Add note to guild's notice board
    """
    return add_note_to_board(message.text, username)


@app.post('/my_guild/show_notes')
async def show_notes(username: str = Depends(oauth2_scheme)) -> Dict[str, List[str]]:
    """
    Show all notes that have been added to board
    """
    return show_all_notes(username)


@app.get('/guilds')
async def show_all_guilds(
    username: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    """
    Get list of existing guilds
    """
    return show_guilds()
