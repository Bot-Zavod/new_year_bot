""" busines logic database access """
from datetime import timedelta
from typing import Dict
from typing import List
from typing import Tuple
from sqlalchemy.orm.session import Session

from . import _admin
from . import _registration
from ..hegai_db import Action
from ..hegai_db import local_time
from ..hegai_db import User
from ..hegai_db import UserAction
from ._utils import local_session


class DBSession(_admin.Mixin, _registration.Mixin):
    """ db function with renewadle session for each func """

    def __init__(self):
        self.action_types = self.get_action_types()
        self.admins = self.get_admins()

    @local_session
    def get_all_users(self, session) -> List:
        """ returns all users """
        users = session.query(User).all()
        return users

    @local_session
    def get_all_users_for_broadcast(self, session) -> List[Tuple[int, bool]]:
        """ returns all users ids and is_banned """
        users = session.query(User.chat_id).all()
        return users

    @local_session
    def get_all_usernames(self, session: Session) -> List:
        """ returns all usernames from db """
        usernames_list = session.query(User.username).all()
        usernames = [username[0] for username in usernames_list]
        return usernames

    @local_session
    def get_all_users_not_used_gift(self, session) -> List[User]:
        """ pass """
        users = session.query(User).filter(User.used_gift_this_month == False).all()
        return users

    @local_session
    def update_used_gift_this_month_set_false(self, session, chat_id):
        """ pass """
        user : User = session.query(User).get(chat_id)
        user.used_gift_this_month = False
        session.commit()

    @local_session
    def update_used_gift_this_month_set_true(self, session, chat_id):
        """ pass """
        user : User = session.query(User).get(chat_id)
        user.used_gift_this_month = True
        session.commit()

    @local_session
    def check_used_gift_this_month(self, session, chat_id):
        """ pass """
        user : User = session.query(User).get(chat_id)
        return user.used_gift_this_month

    @local_session
    def get_user_data(self, session, chat_id: int) -> User:
        """ returns user by chat_id """
        user = session.query(User).get(chat_id)
        return user

    @local_session
    def update_username(self, session, chat_id: int, username: str) -> User:
        """ updates user username if none """
        user = session.query(User).get(chat_id)
        user.username = username
        session.commit()
        user = session.query(User).get(chat_id)
        return user

    @local_session
    def get_user_data_by_username(self, session, username: str) -> User:
        """ returns user by username """
        user = session.query(User).filter(User.username == username).first()
        return user

    @local_session
    def add_time_registered(self, session, chat_id, time):
        """ pass """
        user = session.query(User).get(chat_id)
        user.time_registered = time
        session.commit()

    @local_session
    def count_users(self, session) -> int:
        """ number of users in our db """

        users_quantity = session.query(User).count()
        return users_quantity

    @local_session
    def get_users_list(self, session):
        """ list all users in database """

        users = session.query(User.chat_id).all()
        return users

    @local_session
    def log_action(self, session, chat_id: int, action: str):
        """ log which action has user performed """

        action_id = self.action_types[action]
        new_action = UserAction(user_id=chat_id, action=action_id)
        session.add(new_action)
        session.commit()

    @local_session
    def get_action_types(self, session) -> Dict[str, int]:
        """ cache actions for easier create """

        # reverse name and id
        actions = {
            value: key for key, value in session.query(Action.id, Action.name).all()
        }

        return actions


db_session: DBSession = DBSession()
