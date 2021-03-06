# -*- coding: utf-8 -*-
""" texts for massages """
import json
import os
import re

import pytz


directory_path = os.path.dirname(os.path.abspath(os.path.abspath(__file__)))
new_path = os.path.join(directory_path, "texts.json")

with open(new_path, "r", encoding="utf-8") as fp:
    text = json.load(fp)

start_keyboard = [
    [text["get_gift"]],
    [text["connect_admin"]],
    [text["bot_faq"]],
]

URL_BUTTON_REGEX = re.compile(
    r"\s*~ ((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]"
    r"+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
)
TIMER_RANGE = [6, 10]
REG_TIMER = r"^(\d|\d\d):00 🕓$"
REG_HOURS = re.compile(r"[0-2][0-9]:[0-6][0-9]-[0-2][0-9]:[0-6][0-9]")  # 10:20-04:40
URL_REGEX = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|"
    r"[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)  # 10:20-04:40


kiev_tz = os.getenv("TIME_ZONE", "Europe/Kiev")
TIME_ZONE = pytz.timezone(kiev_tz)

gsheets_gifts = {
    1: "E",
    2: "F",
    3: "G",
    4: "H",
    5: "I",
    6: "J",
    7: "K",
    8: "L",
    9: "M",
    10: "N",
    11: "O",
    12: "P",
}
