
from telegram.ext import CommandHandler
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
import requests
import os 
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
import logging
from dotenv import load_dotenv
load_dotenv()

# TELEGRAM_TOKEN=os.environ.get('TELEGRAM_TOKEN')
# ALERT_URL = os.environ.get('ALERT_URL')
# LOGIN_URL = os.environ.get('LOGIN_URL')
# REGISTER_URL = os.environ.get('REGISTER_URL')

TELEGRAM_TOKEN="5338899788:AAFWvovW2rAuu9CAxixDIPPxm4BF4fRGJS8"
ALERT_URL="https://api-alerts21.herokuapp.com/api/v1/alerts"
LOGIN_URL="https://api-alerts21.herokuapp.com/api/v1/auth/login"
REGISTER_URL="https://api-alerts21.herokuapp.com/api/v1/auth/register"

# enable logging
logging.basicConfig(filename='error.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dp = updater.dispatcher

def is_float(element):
    try:
        float(element)
        return True
    except ValueError:
        return False

def start(update: Update, context: CallbackContext):
    author = update.message.from_user.first_name
    reply = "Hi! {}. Provide information to save an alert".format(author)
    context.bot.send_message(chat_id = update.message.chat_id, text=reply)

def get_alert_info(update, context):
    alert_info = update.message.text.split()
    author = update.message.from_user.first_name
    author = [a.lower() for a in author.split()]
    email = '_'.join(author)+"@alert.com"
    password = '#'+'_'.join(author)+'2022'

    data = {'email': email, 'password': password}

    if alert_info[0] == '/alert':
        alert_info.pop(0)
        currency = alert_info[0]
        threshold = alert_info[1]
        name = " ".join(['Alert',currency])

        if len(alert_info) > 2:
            notes = ' '.join(alert_info[2:])
        else:
            notes = None
            
        if is_float(threshold):
            payload = {"name": name, "type": "PRICE", "currency": currency, "threshold": threshold, 'user_id':2, 'notes':notes}
            
            try:
                print('Before POST request')
                session = requests.Session()
                user = session.post(LOGIN_URL, data=data)
                print('After test login')
                user = user.json()
                print(user)
                if user is None:
                    print('User is None')
                    user = session.post(REGISTER_URL, data=data)
                    user = user.json()
                    payload['user_id'] = user['id']
                    headers = {'Authorization':'Bearer ' + user['access_token']}
                else:
                    print('User is not None')
                    print(user)
                    if user['status'] == 'error':
                        update.message.reply_text(user["message"])
                    else:
                        payload['user_id'] = user['id']
                        headers = {'Authorization':'Bearer ' + user['access_token']}
                            
                r = session.post(ALERT_URL, headers=headers, data=payload)
                print('After POST request')
                r = r.json()
                update.message.reply_text(r["message"])
                update.message.poll()
                print('After send message')
            except Exception as e:
                print('Error when save alert')
                print(e)
        elif threshold[-1] == '%':
            payload = {"name": name, "type": "PERCENT", "currency": currency, "threshold": threshold[:-1], 'user_id':2, 'notes':notes}
            
            try:
                session = requests.Session()
                user = session.post(LOGIN_URL, data=data)
                user = user.json()
                if user is None:
                    user = session.post(REGISTER_URL, data=data)
                    user = user.json()
                    payload['user_id'] = user['id']
                    headers = {'Authorization':'Bearer ' + user['access_token']}
                else:
                    if user['status'] == 'error':
                        update.message.reply_text(user["message"])
                    else:
                        payload['user_id'] = user['id']
                        headers = {'Authorization':'Bearer ' + user['access_token']}
                            
                r = session.post(ALERT_URL, headers=headers, data=payload)
                r = r.json()
                update.message.reply_text(r["message"])
            except Exception as e:
                update.message.reply_text('Error when save alert')

        elif threshold in ['hourly', 'min', 'daily']:
            if threshold == 'hourly':
                print('Je suis dans le bon bloc')
                keyboard = [
                    [
                        InlineKeyboardButton("1 hour", callback_data= email+ ' '+currency+ " 1 hour"),
                        InlineKeyboardButton("2 hours", callback_data= email+ ' '+currency+ " 2 hours")
                    ], 
                    [
                        InlineKeyboardButton("3 hours", callback_data= email+ ' '+currency+ " 3 hours"),
                        InlineKeyboardButton("6 hours", callback_data= email+ ' '+currency+ " 6 hours")
                    ],
                    [
                        InlineKeyboardButton("12 hours", callback_data= email+ ' '+currency+ " 12 hours"),
                    ]
                ]
            elif threshold == 'min':
                keyboard = [
                    [
                        InlineKeyboardButton("1 minute", callback_data= email+ ' '+currency+ " 1 minute"),
                        InlineKeyboardButton("2 minutes", callback_data= email+ ' '+currency+ " 2 minutes")
                    ], 
                    [
                        InlineKeyboardButton("5 minutes", callback_data= email+ ' '+currency+ " 5 minutes"),
                        InlineKeyboardButton("10 minutes", callback_data= email+ ' '+currency+ " 10 minutes")
                    ],
                    [
                        InlineKeyboardButton("15 minutes", callback_data= email+ ' '+currency+ " 15 minutes"),
                        InlineKeyboardButton("30 minutes", callback_data= email+ ' '+currency+ " 30 minutes")
                    ]
                ]
            elif threshold == 'daily':
                keyboard = [
                    [
                        InlineKeyboardButton("1 day", callback_data= email+ ' '+currency+ " 1 day"),
                        InlineKeyboardButton("2 days", callback_data= email+ ' '+currency+ " 2 days")
                    ], 
                    [
                        InlineKeyboardButton("weekly", callback_data= email+ ' '+currency+ " 1 weekly")
                    ]
                ]
            else:
                keyboard = []
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Choose the period length:', reply_markup=reply_markup)
    else:
        update.message.reply_text('No found')      


def button(update: Update, context: CallbackContext):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()
    payload = query.data.split()

    email = payload[0]
    password = '#'+email.split('@')[0]+'2022'

    data = {'email': email, 'password': password}
    payload = {"name": "Alert "+payload[1], "type": "PERIODIC", "currency": payload[1], "threshold": payload[2], 'user_id':None, 'notes':payload[3]} 
    try:
        session = requests.Session()
        user = session.post(LOGIN_URL, data=data)
        user = user.json()
        if user is None:
            user = session.post(REGISTER_URL, data=data)
            user = user.json()
            payload['user_id'] = user['id']
            headers = {'Authorization':'Bearer ' + user['access_token']}
            print(headers)
        else:
            print('User is not None')
            if user['status'] == 'error':
                query.edit_message_text(text=user["message"])
            else:
                print('UserId')
                print(user)
                payload['user_id'] = user['id']
                headers = {'Authorization':'Bearer ' + user['access_token']}
                print(headers)
                r = session.post(ALERT_URL, headers=headers, data=payload)
                r = r.json()
                query.edit_message_text(text=r["message"])
    except Exception as e:
        print('Error on create alert')
        query.edit_message_text(text='Error when save alert')
    
        
def error(update, context):
    logger.error("Update '%s' caused error '%s'", update, update.error)


def echo_sticker(update: Update, context: CallbackContext):
    context.bot.send_sticker(chat_id = update.message.chat_id, sticker=update.message.sticker.file_id)
     
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.sticker, echo_sticker))
dp.add_handler(MessageHandler(Filters.text, get_alert_info))
dp.add_handler(CallbackQueryHandler(button))
dp.add_error_handler(error)

updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get('PORT', 5000)), url_path=TELEGRAM_TOKEN, webhook_url='https://bot-alerts21.herokuapp.com/' + TELEGRAM_TOKEN)    
