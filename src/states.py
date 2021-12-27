""" bot states for conversation handler """
from enum import Enum


class States(Enum):
    """ states keys """

    MENU = 0

    ADMIN_MENU = 1

    ACCOUNT = 2

    ASK_USERNAME = 3

    INTRO = 4

    GREETINGS = 5

    ASK_GIFT = 6

    GET_GIFT = 7

    GET_GIFT_APPROVE = 8
