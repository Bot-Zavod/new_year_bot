""" db for regsistation workflow """
from telegram import Chat

from ..hegai_db import local_time
from ..hegai_db import User
from ._utils import local_session


class Mixin:
    """ registration """

    @local_session
    def add_user(self, session, chat: Chat) -> User:
        """
        Create user record if not exist, otherwise update username
        """
        chat_id = chat.id
        username = chat.username
        first_name = chat.first_name

        user = session.query(User).get(chat_id)
        if user:
            if username:
                if user.username != username:
                    user.username = username
                    session.commit()
            return user

        new_user = User(
            chat_id=chat_id,
            username=username,
            full_name=first_name,
            time_registered=local_time()
        )
        session.add(new_user)
        session.commit()
        return new_user

    @local_session
    def user_is_registered(self, session, chat_id: int) -> bool:
        """
        Create user record if not exist, otherwise update username
        """
        user = session.query(User).get(chat_id)
        if user:
            return True
        return False

    @local_session
    def add_user_data(
        self, session, chat: Chat, username: str, full_name: str
    ):
        """ save user settings """

        chat_id = chat.id

        user = session.query(User).get(chat_id)
        if not user:
            user = self.add_user(chat)
        user.username = username
        user.full_name = full_name
        session.commit()
