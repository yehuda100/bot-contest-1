from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
import db


def bold(text):
    return '<b>' + text + '</b>'


def keyboard_helper(id, status, page=1):
    indicator = {0: '✖️', 1: '✔️'}
    if status == -1:
        status = [0, 1]
    else:
        status = [status]
    tasks = db.task_list(id, status, page)
    keyboard = [[InlineKeyboardButton(indicator[t[1]] + "‏‏‏  " + t[2][:25], callback_data=t[0])]for t in tasks]
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
