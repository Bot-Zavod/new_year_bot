from datetime import date
import pygsheets
import re

from ..data import gsheets_gifts

gc = pygsheets.authorize(client_secret="client_secret_408492841241-evs06jqucilc81k2vdii5e83nq0l4d28.apps.googleusercontent.com.json")

# Open spreadsheet and then worksheet
sh = gc.open('Чат-бот_Подарки от Trust PR Production')
wks = sh.sheet1

def get_usernames():
    cell_list = wks.range('C2:C54')
    usernames = []
    for cell in cell_list:
        cell = cell[0]
        try:
            username = cell.value.replace("@", "")
        except AttributeError:
            username = cell.value
        usernames.append(username)
    return usernames


def get_greeting(username):
    cell_list = wks.range('C2:C54')

    row = None
    for cell in cell_list:
        cell = cell[0]
        if username != None:
            if username == cell.value.replace("@", ""):
                row = cell.row

    if row != None:
        greeting = wks.cell(f"D{row}")
        greeting = greeting.value
        return greeting
    else:
        return None


def get_available_nums(username):
    cell_list = wks.range('C2:C54')

    row = None
    for cell in cell_list:
        cell = cell[0]
        if username != None:
            if username == cell.value.replace("@", ""):
                row = cell.row

    if row != None:
        available_nums = []
        cell_list = wks.range(f'E{row}:P{row}')
        for cell in cell_list[0]:
            if cell.color == (None, None, None, None) and cell.value != '':
                available_nums.append(cell.col-4)
        return available_nums
    else:
        return None


def sheets_get_gift(username, num):
    cell_list = wks.range('C2:C54')

    for cell in cell_list:
        cell = cell[0]
        if username == cell.value.replace("@", ""):
            row = cell.row

    gift = wks.cell(f"{gsheets_gifts[num]}{row}")
    return gift.value


def mark_used_gift(username, num):
    cell_list = wks.range('C2:C54')

    for cell in cell_list:
        cell = cell[0]
        if username == cell.value.replace("@", ""):
            row = cell.row

    gift = wks.cell(f"{gsheets_gifts[num]}{row}")
    gift.color = (1, 1, 0, 0)
    gift.update()
    return None
