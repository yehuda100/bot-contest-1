from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import *
from helpers import *
import logging
import bot_token
import db


GET_TASK = 1
CHOOSE_TASK, CHOOSE_ACTION, EDIT_TASK = 10, 11, 12
END = ConversationHandler.END


KEYBOARD = [[InlineKeyboardButton('להוסיף משימה', callback_data='add')],
[InlineKeyboardButton('משימות שבוצעו', callback_data='done'),
InlineKeyboardButton('משימות שלא בוצעו', callback_data='not_done')],
[InlineKeyboardButton('כל המשימות', callback_data='all')]]

MAIN_MENU = [[InlineKeyboardButton('תפריט ראשי', callback_data='main_menu')]]


def start(update, context):
    if db.is_new_user(update.effective_user.id):
        db.add_user(update.effective_user.id)
    keyboard = [[InlineKeyboardButton('להוסיף משימה', callback_data='add')]]
    if db.user_have_tasks(update.effective_user.id):
        keyboard = KEYBOARD
    update.message.reply_text("שלום {} מה תרצה שנעשה היום?".format(update.effective_user.first_name),
    reply_markup=InlineKeyboardMarkup(keyboard))

def add(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text('שלח לי את המשימה שברצונך להוסיף:\n\
    לביטול שלח /cancel .')
    return GET_TASK

def get_task(update, context):
    db.add_task(id=update.effective_user.id, task=update.message.text)
    update.message.reply_text('המשימה נוספה בהצלחה!',
    reply_markup=InlineKeyboardMarkup(KEYBOARD))
    return END

def all_tasks(update, context):
    query = update.callback_query
    query.answer()
    context.user_data['status'] = -1
    keyboard = keyboard_helper(update.effective_user.id, context.user_data['status']) + MAIN_MENU
    query.edit_message_text('בחר משימה כדי לבצע פעולות:',
    reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_TASK

def not_done_tasks(update, context):
    query = update.callback_query
    query.answer()
    context.user_data['status'] = 0
    if db.not_done_tasks_exists(update.effective_user.id):
        keyboard = keyboard_helper(update.effective_user.id, context.user_data['status']) + MAIN_MENU
        query.edit_message_text('בחר משימה כדי לבצע פעולות:',
        reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSE_TASK
    else:
        query.edit_message_text('לא נמצאו משימות מתאימות, שנה סטטוס של משימות קיימות כדי שיוכלו להתאים.',
        reply_markup=InlineKeyboardMarkup(KEYBOARD))

def done_tasks(update, context):
    query = update.callback_query
    query.answer()
    context.user_data['status'] = 1
    if db.done_tasks_exists(update.effective_user.id):
        keyboard = keyboard_helper(update.effective_user.id, context.user_data['status']) + MAIN_MENU
        query.edit_message_text('בחר משימה כדי לבצע פעולות:',
        reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSE_TASK
    else:
        query.edit_message_text('לא נמצאו משימות מתאימות, שנה סטטוס של משימות קיימות כדי שיוכלו להתאים.',
        reply_markup=InlineKeyboardMarkup(KEYBOARD))

def choose_task(update, context):
    query = update.callback_query
    query.answer()
    context.user_data['task_id'] = int(query.data)
    task = db.get_task(int(query.data))
    keyboard = [[InlineKeyboardButton('מחק משימה', callback_data='delete')],
    [InlineKeyboardButton('ערוך משימה', callback_data='edit')]]
    if task[1] == 0:
        keyboard = [[InlineKeyboardButton('סמן כבוצע', callback_data='change=1')]] + keyboard
    else:
        keyboard = [[InlineKeyboardButton('סמן כלא בוצע', callback_data='change=0')]] + keyboard
    query.edit_message_text('{}\nבחר מה ברצונך לבצע:'.format(bold(task[0])),
    reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_ACTION

def change_status(update, context):
    query = update.callback_query
    query.answer()
    db.change_status(context.user_data['task_id'], int(query.data[-1]))
    if context.user_data['status'] == -1:
        keyboard = keyboard_helper(update.effective_user.id, context.user_data['status']) + MAIN_MENU
        query.edit_message_text('בחר משימה כדי לבצע פעולות:',
        reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSE_TASK
    elif context.user_data['status'] == 0:
        if db.not_done_tasks_exists(update.effective_user.id):
            keyboard = keyboard_helper(update.effective_user.id, context.user_data['status']) + MAIN_MENU
            query.edit_message_text('בחר משימה כדי לבצע פעולות:',
            reply_markup=InlineKeyboardMarkup(keyboard))
            return CHOOSE_TASK
        else:
            query.edit_message_text('לא נמצאו משימות מתאימות, שנה סטטוס של משימות קיימות כדי שיוכלו להתאים.',
            reply_markup=InlineKeyboardMarkup(KEYBOARD))
            return END
    elif context.user_data['status'] == 1:
        if db.done_tasks_exists(update.effective_user.id):
            keyboard = keyboard_helper(update.effective_user.id, context.user_data['status']) + MAIN_MENU
            query.edit_message_text('בחר משימה כדי לבצע פעולות:',
            reply_markup=InlineKeyboardMarkup(keyboard))
            return CHOOSE_TASK
        else:
            query.edit_message_text('לא נמצאו משימות מתאימות, שנה סטטוס של משימות קיימות כדי שיוכלו להתאים.',
            reply_markup=InlineKeyboardMarkup(KEYBOARD))
            return END

def delete(update, context):
    query = update.callback_query
    query.answer()
    db.delete(context.user_data['task_id'])
    if context.user_data['status'] == -1:
        if db.user_have_tasks(update.effective_user.id):
            keyboard = keyboard_helper(update.effective_user.id, context.user_data['status']) + MAIN_MENU
            query.edit_message_text('בחר משימה כדי לבצע פעולות:',
            reply_markup=InlineKeyboardMarkup(keyboard))
            return CHOOSE_TASK
        else:
            keyboard = [[InlineKeyboardButton('להוסיף משימה', callback_data='add')]]
            query.edit_message_text("שלום {} מה תרצה שנעשה היום?".format(update.effective_user.first_name),
            reply_markup=InlineKeyboardMarkup(keyboard))
            return END
    elif context.user_data['status'] == 0:
        if db.not_done_tasks_exists(update.effective_user.id):
            keyboard = keyboard_helper(update.effective_user.id, context.user_data['status']) + MAIN_MENU
            query.edit_message_text('בחר משימה כדי לבצע פעולות:',
            reply_markup=InlineKeyboardMarkup(keyboard))
            return CHOOSE_TASK
        else:
            query.edit_message_text('לא נמצאו משימות מתאימות, שנה סטטוס של משימות קיימות כדי שיוכלו להתאים.',
            reply_markup=InlineKeyboardMarkup(KEYBOARD))
            return END
    elif context.user_data['status'] == 1:
        if db.done_tasks_exists(update.effective_user.id):
            keyboard = keyboard_helper(update.effective_user.id, context.user_data['status']) + MAIN_MENU
            query.edit_message_text('בחר משימה כדי לבצע פעולות:',
            reply_markup=InlineKeyboardMarkup(keyboard))
            return CHOOSE_TASK
        else:
            query.edit_message_text('לא נמצאו משימות מתאימות, שנה סטטוס של משימות קיימות כדי שיוכלו להתאים.',
            reply_markup=InlineKeyboardMarkup(KEYBOARD))
            return END

def edit(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text('שלח את הטקסט החדש:')
    return EDIT_TASK

def edit_task(update, context):
    db.edit_task(context.user_data['task_id'], update.message.text)
    keyboard = keyboard_helper(update.effective_user.id, context.user_data['status']) + MAIN_MENU
    update.message.reply_text('המשימה נערכה בהצלחה!',
    reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_TASK

def next_page(update, context):
    query = update.callback_query
    query.answer()
    page = int(query.data[5:])
    keyboard = keyboard_helper(update.effective_user.id, context.user_data['status'], page) + MAIN_MENU
    query.edit_message_text('בחר משימה כדי לבצע פעולות:',
    reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_ACTION

def prev_page(update, context):
    query = update.callback_query
    query.answer()
    page = int(query.data[5:])
    keyboard = keyboard_helper(update.effective_user.id, context.user_data['status'], page) + MAIN_MENU
    query.edit_message_text('בחר משימה כדי לבצע פעולות:',
    reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_ACTION

def main_menu(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton('להוסיף משימה', callback_data='add')]]
    if db.user_have_tasks(update.effective_user.id):
        keyboard = KEYBOARD
    query.edit_message_text("שלום {} מה תרצה שנעשה היום?".format(update.effective_user.first_name),
    reply_markup=InlineKeyboardMarkup(keyboard))
    return END

def cancel(update, context):
    keyboard = [[InlineKeyboardButton('להוסיף משימה', callback_data='add')]]
    if db.user_have_tasks(update.effective_user.id):
        keyboard = KEYBOARD
    update.message.reply_text("שלום {} מה תרצה שנעשה היום?".format(update.effective_user.first_name),
    reply_markup=InlineKeyboardMarkup(keyboard))
    return END


def main():

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
    logger = logging.getLogger(__name__)

    defaults = Defaults(parse_mode=ParseMode.HTML)
    updater = Updater(bot_token.TOKEN, use_context=True, defaults=defaults)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))

    dp.add_handler(ConversationHandler(
    entry_points=[CallbackQueryHandler(add, pattern='add')],
    states={GET_TASK: [MessageHandler(Filters.text & ~Filters.command, get_task)]},
    fallbacks=[CommandHandler('cancel', cancel)]))

    dp.add_handler(ConversationHandler(
    entry_points=[CallbackQueryHandler(all_tasks, pattern='all'),
    CallbackQueryHandler(not_done_tasks, pattern='not_done'),
    CallbackQueryHandler(done_tasks, pattern='done')],
    states={CHOOSE_TASK: [CallbackQueryHandler(choose_task, pattern='^[0-9]+$')],
    CHOOSE_ACTION: [CallbackQueryHandler(change_status, pattern='^change=[0-1]$'),
    CallbackQueryHandler(delete, pattern='^delete$'),
    CallbackQueryHandler(edit, pattern='^edit$')],
    EDIT_TASK: [MessageHandler(Filters.text & ~Filters.command, edit_task)]},
    fallbacks=[CallbackQueryHandler(next_page, pattern='^next=[0-9]+$'),
    CallbackQueryHandler(prev_page, pattern='^prev=[0-9]+$'),
    CallbackQueryHandler(main_menu, pattern='main_menu'),
    CommandHandler('cancel', cancel)], allow_reentry=True))


    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
  main()




#by t.me/yehuda100
