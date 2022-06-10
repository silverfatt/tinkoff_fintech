from typing import Any, Dict, List

from app.database import Guild, GuildNotes, Soldier, User, Warehouse, create_session

NO_GUILD = '%_no_guild_%'


def c_guild(guild_name: str, username: str) -> Dict[str, str]:
    """
    Create new guild and add it to database
    :param guild_name: name of new guild
    :param username: user who tries to create a guild
    :return: result of operation
    """
    with create_session() as session:
        guild_query = session.query(Guild).filter(Guild.name == guild_name)
        if session.query(guild_query.exists()).scalar():
            return {'error': 'already exists'}
        user = session.query(User).filter(User.login == username).one()
        if user.guild != NO_GUILD:
            return {'error': 'you are already a member of guild'}
        if user.money < 1000:
            return {'error': 'not enough money'}
        user.money -= 1000
        user.guild = guild_name
        user.rank = 'leader'
        new_guild = Guild(name=guild_name)
        session.add(new_guild)
        session.commit()
        return {'result': f'guild {guild_name} succesfully created!'}


def j_guild(guild_name: str, username: str) -> Dict[str, str]:
    """
    Sets new guild in database for user
    :param guild_name: name of guild to join
    :param username: user who tries to join a guild
    :return: result of operation
    """
    with create_session() as session:
        guild_query = session.query(Guild).filter(Guild.name == guild_name)
        if not session.query(guild_query.exists()).scalar():
            return {'error': 'guild does not exist'}
        user = session.query(User).filter(User.login == username).one()
        user.guild = guild_name
        session.commit()
        return {'result': f'wellcome to {guild_name}!'}


def show_my_guild(username: str) -> Dict[str, str]:
    """
    Get dictionary of player's guild members
    :param username: user who tries to get dictionary
    :return: dictionary of players or error message
    """
    with create_session() as session:
        user = session.query(User).filter(User.login == username).one()
        if user.guild != NO_GUILD:
            users = session.query(User).filter(User.guild == user.guild).all()
            users_dictionary = {
                user.login: 'HQ level: ' + str(user.HQ_level) + ' rank: ' + user.rank
                for user in users
            }
            return users_dictionary
        return {'error': 'you are not a member of a guild'}


def send_res(money: int, food: int, send_to: str, username: str) -> Dict[str, str]:
    """
    Send resources to another player (guild member) and change values in database
    :param money: amount of money to send
    :param food: amount of food to send
    :param send_to: nickname of addressee
    :param username: user who tries to send resources
    :return: result of operation
    """
    with create_session() as session:
        if username == send_to:
            return {'error': 'you cannot trade with yourself!'}
        user_query = session.query(User.id).filter(User.login == send_to)
        if session.query(user_query.exists()).scalar():
            user1 = session.query(User).filter(User.login == username).one()
            if user1.guild == NO_GUILD:
                return {'error': 'you are not a member of any guild'}
            user2 = session.query(User).filter(User.login == send_to).one()
            if user2.guild != user1.guild:
                return {'error': 'user is not a member of your guild'}
            warehouses = session.query(Warehouse).all()
            if user1.money >= money and user1.food >= food:
                if (user2.money + money) <= warehouses[
                    user2.Wh_level - 1
                ].capacity and (user2.food + food) <= warehouses[
                    user2.Wh_level - 1
                ].capacity:
                    user1.money -= money
                    user1.food -= food
                    user2.money += money
                    user2.food += food
                    session.commit()
                    return {'result': 'success'}
                return {'error': 'reciever has not enough space in warehouse'}
            return {'error': "you don't have enough resourses"}
        return {'error': 'user does not exist'}


def kick(member_to_kick: str, username: str) -> Dict[str, str]:
    """
    Kick other player from guild
    :param member_to_kick: nickname of player who is going to be kicked
    :param username: user who tries to kick
    :return: result of operation
    """
    with create_session() as session:
        if username == member_to_kick:
            return {'error': 'you cannot kick yourself!'}
        user_query = session.query(User.id).filter(User.login == member_to_kick)
        if session.query(user_query.exists()).scalar():
            user1 = session.query(User).filter(User.login == username).one()
            if user1.guild == NO_GUILD:
                return {'error': 'you are not a member of any guild'}
            user2 = session.query(User).filter(User.login == member_to_kick).one()
            if user2.guild != user1.guild:
                return {'error': 'user is not a member of your guild'}
            if user1.rank != 'leader':
                return {'error': 'only leader can kick players'}
            user2.guild = NO_GUILD
            session.commit()
            return {'result': 'success'}
        return {'error': 'user does not exist'}


def leave(username: str) -> Dict[str, str]:
    """
    Leave from guild and destroy it is player "username" was a leader
    :param username: user whi tries to leave a guild
    :return: result of operation
    """
    with create_session() as session:
        user = session.query(User).filter(User.login == username).one()
        if user.guild == NO_GUILD:
            return {'error': 'you are not a member of any guild'}
        if user.rank == 'member':
            user.guild = NO_GUILD
            session.commit()
            return {'result': 'successfully left'}
        user.rank = 'leader'
        members = session.query(User).filter(User.guild == user.guild).all()
        session.query(Guild).filter(Guild.name == user.guild).delete()
        for member in members:
            member.guild = NO_GUILD
        session.commit()
        return {'result': 'success'}


def transfer_leadership(new_leader: str, username: str) -> Dict[str, str]:
    """
    Make other user a leader and make changes in database
    :param new_leader: new leader's nickname
    :param username: user who tries to transfer leadership
    :return: result of operation
    """
    with create_session() as session:
        if username == new_leader:
            return {'error': 'you cannot transfer leadership to yourself'}
        user_query = session.query(User.id).filter(User.login == new_leader)
        if session.query(user_query.exists()).scalar():
            user1 = session.query(User).filter(User.login == username).one()
            if user1.guild == NO_GUILD:
                return {'error': 'you are not a member of any guild'}
            user2 = session.query(User).filter(User.login == new_leader).one()
            if user1.guild != user2.guild:
                return {'error': 'user is not a member of your guild'}
            user1.rank = 'member'
            user2.rank = 'leader'
            session.commit()
            return {'result': 'success'}
        return {'error': 'no such player'}


def show_guilds() -> Dict[str, List[str]]:
    """
    :return: dictionary of existing guilds
    """
    with create_session() as session:
        guilds = session.query(Guild).filter(Guild.name != NO_GUILD).all()
        guilds_dictionary = {'guilds': [guild.name for guild in guilds]}
        return guilds_dictionary


def send_reinforcements_to_ally(
    level: int, amount: int, send_to: str, username: str
) -> Dict[str, str]:
    """
    Transfer some soldiers to username's guild member
    :param level: soldier's tier
    :param amount: amount of soldiers
    :param send_to: nickname of addressee
    :param username: user who tries to transfer army
    :return: result of operation
    """
    with create_session() as session:
        if username == send_to:
            return {'error': 'you cannot trade with yourself!'}
        user_query = session.query(User.id).filter(User.login == send_to)
        if session.query(user_query.exists()).scalar():
            user1 = session.query(User).filter(User.login == username).one()
            if user1.guild == NO_GUILD:
                return {'error': 'you are not a member of any guild'}
            user2 = session.query(User).filter(User.login == send_to).one()
            if user2.guild != user1.guild:
                return {'error': 'user is not a member of your guild'}
            soldiers = session.query(Soldier).all()
            if level == 1:
                if user1.soldiers_t1 < amount:
                    return {'error': 'not enough soldiers'}
                user1.soldiers_t1 -= amount
                user2.soldiers_t1 += amount
            elif level == 2:
                if user1.soldiers_t2 < amount:
                    return {'error': 'not enough soldiers'}
                user1.soldiers_t2 -= amount
                user2.soldiers_t2 += amount
            elif level == 3:
                if user1.soldiers_t3 < amount:
                    return {'error': 'not enough soldiers'}
                user1.soldiers_t3 -= amount
                user2.soldiers_t3 += amount
            elif level == 4:
                if user1.soldiers_t4 < amount:
                    return {'error': 'not enough soldiers'}
                user1.soldiers_t4 -= amount
                user2.soldiers_t4 += amount
            elif level == 5:
                if user1.soldiers_t5 < amount:
                    return {'error': 'not enough soldiers'}
                user1.soldiers_t5 -= amount
                user2.soldiers_t5 += amount
            user1.army_power -= amount * soldiers[level - 1].power
            user1.all_power -= amount * soldiers[level - 1].power
            user2.army_power += amount * soldiers[level - 1].power
            user2.all_power += amount * soldiers[level - 1].power
            session.commit()
            return {'result': 'success'}
        return {'error': 'user does not exist'}


def add_note_to_board(text: str, username: str) -> Dict[str, str]:
    """
    Add note to database
    :param text: note's text
    :param username: user who tries to add note
    :return: result of operation
    """
    with create_session() as session:
        user = session.query(User).filter(User.login == username).one()
        if user.guild == NO_GUILD:
            return {'error': 'you are not a member of a guild'}
        guild_notes = GuildNotes(sender=username, guildname=user.guild, text=text)
        session.add(guild_notes)
        return {'result': 'success'}


def show_all_notes(username: str) -> Dict[str, Any]:
    """
    Returns dictionary of username's guild notes
    :param username: user who tries to get notes
    :return: dictionary of notes
    """
    with create_session() as session:
        user = session.query(User).filter(User.login == username).one()
        if user.guild == NO_GUILD:
            return {'error': 'you are not a member of a guild'}
        guild_notes = (
            session.query(GuildNotes).filter(GuildNotes.guildname == user.guild).all()
        )
        notes_dictionary = {
            user.guild: [f'{note.sender}:  {note.text}' for note in guild_notes]
        }
        return notes_dictionary
