""" busines logic database access """
from datetime import timedelta
from typing import Dict
from typing import List
from typing import Tuple

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
    def get_all_usernames(self, session) -> List:
        """ returns all usernames from db """
        usernames_list = session.query(User.username).all()
        usernames = [username[0] for username in usernames_list]
        return usernames

    @local_session
    def get_user_data(self, session, chat_id: int) -> User:
        """ returns user by chat_id """
        user = session.query(User).get(chat_id)
        return user

    @local_session
    def get_user_data_by_username(self, session, username: str) -> User:
        """ returns user by username """
        user = session.query(User).filter(User.username == username).first()
        return user

    @local_session
    def update_last_time_gift(self, session, chat_id):
        """ updates the last time a user got a gift """
        user = session.query(User).get(chat_id)
        user.last_time_gift = local_time()
        session.commit()

    @local_session
    def check_last_time_gift(self, session, chat_id):
        """ checks whether it has been 30 days since the last time a user got a gift """
        user = session.query(User).get(chat_id)
        try:
            diff = local_time() - user.last_time_gift
        except TypeError:
            return True
        if diff > timedelta(days=30):
            return True
        else:
            return False

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
