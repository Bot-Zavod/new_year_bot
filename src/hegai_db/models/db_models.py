""" database models """
from datetime import datetime
from enum import Enum
from typing import Any

import pytz
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean

meta = MetaData(  # automatically name constraints to simplify migrations
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)
# Any saves from mypy checks of a dynamic class
Base: Any = declarative_base(metadata=meta)


def local_time() -> datetime:
    """ time in Ukraine """
    kiev_tz = pytz.timezone("Europe/Kiev")
    current_time = datetime.now(tz=kiev_tz)
    return current_time


class User(Base):
    """ user model """

    __tablename__ = "user"

    chat_id = Column(BigInteger, primary_key=True)
    username = Column(String(35))  # Telegram allows username no longer then 32
    full_name = Column(String)  # full name is unlimited
    used_gift_this_month = Column(Boolean, default=False, nullable=False)
    time_registered = Column(DateTime(timezone=True), default=local_time)

    def __repr__(self):
        return "<User(chat_id='{}', username='{}', full_name='{}')>".format(
            self.chat_id, self.username, self.full_name
        )


class Admin(Base):
    """ admin model """

    __tablename__ = "admin"

    chat_id = Column(Integer, ForeignKey("user.chat_id"), primary_key=True)

    def __repr__(self):
        return "<Admin(chat_id='{}')>".format(self.chat_id)


class Permission(Enum):
    """ helper class to define json keys for role permissions """

    STAT: str = "statistics"
    AD: str = "advertising"
    PARSE: str = "parsing"
    PUSH: str = "push"
    DROP: str = "drop_user"
    SET: str = "set_user"


class UserAction(Base):
    """ user_action model """

    __tablename__ = "user_action"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user.chat_id"))
    action = Column(Integer, ForeignKey("action.id"))
    time_clicked = Column(DateTime(timezone=True), default=local_time)

    user = relationship("User", backref="user_action", foreign_keys=[user_id])
    action_name = relationship(
        "Action", backref="user_action_name", foreign_keys=[action]
    )

    def __repr__(self):
        return "<Action(id='{}', chat_id='{}', action='{}', time='{}')>".format(
            self.id, self.user_id, self.action, self.time_clicked
        )


class Action(Base):
    """ action model """

    __tablename__ = "action"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    # static defenition for insertion safety
    now = "now"
    ban = "ban"
    profile = "profile"
    share = "share"

    def __repr__(self):
        return "<ActionType(id='{}', name='{}')>".format(self.id, self.name)
