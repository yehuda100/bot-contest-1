from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
import db


def bold(text: str) -> str:
    return '<b>' + text.replace('<', '\<').replace('>', '\>') + '</b>'


def keyboard_helper(id: int, status: list, page: int=1) -> list:
    indicator = {0: '✖️', 1: '✔️'}
    tasks = db.task_list(id, status, page)
    keyboard = [[InlineKeyboardButton(indicator[t[1]] + "‏  " + t[2][:25], callback_data=t[0])]for t in tasks]
    if page == 1:
        if db.task_count(id, status) > page * 10:
            keyboard.append([InlineKeyboardButton('הבא', callback_data='next=' + str(page + 1))])
    else:
        if db.task_count(id, status) <= page * 10:
            keyboard.append([InlineKeyboardButton('הקודם', callback_data='prev=' + str(page - 1))])
        else:
            keyboard.append([InlineKeyboardButton('הקודם', callback_data='prev=' + str(page - 1)),
            InlineKeyboardButton('הבא', callback_data='next=' + str(page + 1))])
    return keyboard


#by t.me/yehuda100
