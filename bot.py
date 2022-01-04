#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from functools import wraps
from collections import OrderedDict
import locale
import time
import _thread as thread
import requests
import re
import os
import pickle

import datetime
from report import Doch1_Report

DATE_SELECT, PERSON_SELECT, STATUS_SELECT, NOTE_OUT_OF_BASE_SELECT, CANCEL_SELECT = range(1,6)
CANCEL_TYPE_SEND_CONFS, CANCEL_TYPE_DEFAULT_CONFIGS, CANCEL_TYPE_SEND_DATE = range(1,4)

"""
#Hova
01::נמצא ביחידה
	01:נוכח
02::מחוץ ליחידה
	05:בתפקיד מחוץ ליחידה
	25:כוננות
	09:אחרי תורנות \ משמרת
	03:עובד משמרות
	13:הפניה רפואית
	08:יום סידורים-חייל בודד
	16:משמרת ערב
	19:נגרע ממתין לקליטה
	02:אבט"ש
	14:לימודים על סמך אישור
	20:סבב קו
	23:יום פרט
03::מסופח ליחידה אחרת 
	01:מסופח ליחידה אחרת
04::חופשה שנתית 
	01:חופשה שנתית
	06:חג עדתי
	11:אזכרה - קרבה ראשונה
05::חופשת מחלה
	01:חופשת מחלה (גימלים)
	08:יום ד
	16:שמירת הריון 
06::בקורס \ בהכשרה
	01:בקורס \ בהכשרה
07::נעדר משרות שלא ברשות
	01:נפקד
	02:חשש לנפקדות
	03:מחלה בנפקדות
08::כלוא
	04:עבודות שרות צבאיות
	01:בבסיס כליאה מעצר
	02:עצור בכלא אזרחי
	03:מעצר בית
09::מאושפז
	01:מאושפז
12::חופשה מיוחדת
	04:חופשה מפקד מיוחדת בהכשרה ראשונית
	07:מיוחדת ע"ח שנתית - חובה
	08:חופשת ממתינים
	02:מיוחדת ע"ח המערכת - חובה
	03:אבל - חיילי חובה
13::חו"ל
	02:חו"ל בתפקיד
	04:חו"ל במיוחדת
	22:חו"ל דח"ש/חל"ת
	27:חו"ל - מחלה
	28:חו"ל בחופשה (חובה)
17::בידוד
	17:מחלה שנתית
	18:בידוד ביחידה

### Keva
01::נמצא ביחידה
	01:נוכח
02::מחוץ ליחידה
	05:בתפקיד מחוץ ליחידה
	25:כוננות
	09:אחרי תורנות \ משמרת
	03:עובד משמרות
	13:הפניה רפואית
	16:משמרת ערב
	19:נגרע ממתין לקליטה
	02:אבט"ש
	14:לימודים על סמך אישור
	18:הצ"ח
	20:סבב קו
	15:השעייה בתפקיד
	23:יום פרט
03::מסופח ליחידה אחרת 
	01:מסופח ליחידה אחרת
04::חופשה שנתית 
	01:חופשה שנתית
	04:חופשת אבל - קבע
	06:חג עדתי
	10:חופשה ללא תשלום קצרה
	11:אזכרה - קרבה ראשונה
	13:חופשה צבורה
05::חופשת מחלה
	01:חופשת מחלה (גימלים)
	02:מחלה עפ"י הצהרה
	07:טיפול רפואי
	03:מחלת ילד
	04:מחלת הורה
	16:שמירת הריון 
	05:מחלת בן\בת זוג
	09:מחלת ילד ממארת
	10:מחלת בן זוג ממארת
	11:הריון או לידת בת זוג
	12:תרומת מח עצם / איברים
	14:הורה לבעל מוגבלויות
	15:מחלה בפציעה בתפקיד
06::בקורס \ בהכשרה
	01:בקורס \ בהכשרה
07::נעדר משרות שלא ברשות
	01:נפקד
	02:חשש לנפקדות
	03:מחלה בנפקדות
08::כלוא
	04:עבודות שרות צבאיות
	01:בבסיס כליאה מעצר
	02:עצור בכלא אזרחי
	03:מעצר בית
09::מאושפז
	01:מאושפז
12::חופשה מיוחדת
	05:חופשה מיוחדת - קבע
	06:חופשה מיוחדת - התמחות
13::חו"ל
	02:חו"ל בתפקיד
	04:חו"ל במיוחדת
	22:חו"ל דח"ש/חל"ת
	27:חו"ל - מחלה
	01:חו"ל בחופשה אנשי קבע
17::בידוד
	17:מחלה שנתית
	18:בידוד ביחידה
	19:ע"ח חופשה שנתית
	20:עבודה מהבית
20::חופשת לידה
	01:חופשת לידה
	05:חופשת לידה - חו"ל
    """
# Code: ['Description', 'Main code', 'Secondary code']
possible_statuses = {
    '01':['נמצא ביחידה נוכח', '01', '01'],
    '02':['הגנש/אבטש', '02', '02'],
    '03':['מחוץ ליחידה בתפקיד', '02', '05'],
    '04':['הפנייה רפואית', '02', '13'],
    '05':['חופשה שנתית', '04', '01'],
    '06':['חופשה צבורה - קבע', '04', '13'],
    '07':['אזכרה (דרגה ראשונה)', '04', '11'],
    '08':['גימלים (רופא)', '05', '01'],
    '09':['יום ד\' (החלטת מפקד) - חובה', '05', '08'],
    '10':['מחלה (הצהרה) - קבע', '05', '02'],
    '11':['בקורס/הכשרה', '06', '01'],
    '12':['חו"ל בתפקיד', '13', '02'],
    '13':['חו"ל במיוחדת', '13', '04'],
    '14':['חו"ל בחופשה - קבע', '13', '01'],
    '15':['חו"ל בחופשה - חובה', '13', '28'],
    '16':['יום סידורים חייל בודד', '02', '08'],
    '17':['מסופח ליחידה אחרת', '03', '01'],
    '18':['מיוחדת ע"ח המערכת - חובה', '12', '02'],
    '19':['מיוחדת ע"ח חופשה שנתית - חובה', '12', '07'],
    '20':['אבל - חובה', '12', '03'],
    '21':['בידוד - מחלה שנתית', '17', '17'],
    '22':['בידוד - ביחידה', '17', '18'],
    '23':['בידוד - ע"ח חופשה שנתית - קבע', '17', '19'],
}


START_TIME = datetime.time(8, 0, 0)
END_TIME = datetime.time(10, 30, 0)

custom_keyboard = [[KeyboardButton('/send_today')], [KeyboardButton('/show_future_config')], [KeyboardButton('/toggle_auto_send'), KeyboardButton('/change_future_config')], [KeyboardButton('/cancel_future_config')],]
reply_markup = ReplyKeyboardMarkup(custom_keyboard)
remove_markup = ReplyKeyboardRemove()

user_config = {}
future_dates = {}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def restricted(func):
    @wraps(func)
    def wrapped(updater, context, *args, **kwargs):
        chat_id = updater.message.chat.id
        if str(chat_id) != user_config['telegram_chat_id']:
            print('Unauthorized access denied for chat {}.'.format(chat_id))
            updater.bot.send_message(chat_id=user_config['telegram_chat_id'], text='Unauthorized access denied for chat {}.'.format(user_id))
            return
        return func(updater, context, *args, **kwargs)
    return wrapped

def time_in_range(time, start, end):
    """Return true if x is in the range [start, end]"""
    return start.hour <= time.hour <= end.hour
    
def can_send_now():
    now = datetime.datetime.now()
    return time_in_range(now, START_TIME, END_TIME) and now.isoweekday() not in [5,6]

def setup_one_identity_routine(*args):
    updater = args[0]
    while True:
        delete_conf_cache_old_dates()
        now = datetime.datetime.now()
        # check if time to send doch 1, if yes do, if no, sleep
        if can_send_now() and (now.date() in conf_cache['send_dates'] or conf_cache['always_send']):
            updater.bot.send_message(chat_id=user_config['telegram_chat_id'], text='Auto sending today\'s report: {date}'.format(date=now.date()))
            print('שולח בצורה אוטומטית את הדוח של היום: {date}'.format(date=now.date()))
            report = Doch1_Report(user_config)
            updater.bot.send_message(chat_id=user_config['telegram_chat_id'], text='משיג רשימת חיילים')
            res = report.login_and_get_soldiers()
            if not res[0]:
                updater.bot.send_message(chat_id=user_config['telegram_chat_id'], text=res[1])
            res = send_report(report, res[1])
            updater.bot.send_message(chat_id=user_config['telegram_chat_id'], text='Sent report:\n{report}'.format(report=res))
        else:
            print('Waiting for next time to report')
        # calc time until 8:00 am and sleep
        now = datetime.datetime.now()
        time_to_sleep = (datetime.timedelta(hours=24) - (now-now.replace(hour=START_TIME.hour, minute=START_TIME.minute, second=START_TIME.second))).total_seconds() % (24 * 3600)
        print('Sleeping for {} hours'.format(time_to_sleep/60/60))
        time.sleep(time_to_sleep)

@restricted
def unknown_command(updater, context):
    updater.message.reply_text(text='לא הבנתי...', reply_markup=reply_markup)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def initialize_user_config(path='config.json'):
    global user_config
    
    with open(path, 'rb') as f:
        data = f.read()
    
    user_config = json.loads(data)
    """
    Todo: implement cookies cache file
    
    global cookies_cache
    if os.path.exists(cookie_cache_path):
        with open(cookie_cache_path, 'rb') as f:
            cookies_cache = pickle.load(f)
    """

def initialize_conf_cache(conf_cache_path='conf.cache'):
    global conf_cache
    
    if os.path.exists(conf_cache_path):
        with open(conf_cache_path, 'rb') as f:
            conf_cache = pickle.load(f)
    else:
        conf_cache={}
        conf_cache['send_dates']=[]
        conf_cache['send_confs']={}
        conf_cache['always_send'] = False
        conf_cache['default_configs'] = {}
        write_to_conf_cache(conf_cache_path)

def write_to_conf_cache(conf_cache_path='conf.cache'):
    with open(conf_cache_path, 'wb') as f:
        pickle.dump(conf_cache, f, protocol=pickle.HIGHEST_PROTOCOL)
        
def delete_conf_cache_old_dates():
    to_delete = []
    for date in conf_cache['send_confs']:
        if date < datetime.datetime.today().date():
            to_delete.append(date)
    for date in to_delete:
        del conf_cache['send_confs'][date]
        
    to_delete = []
    for date in conf_cache['send_dates']:
        if date < datetime.datetime.today().date():
            to_delete.append(date)
    for date in to_delete:
        conf_cache['send_dates'].remove(date)
    
    write_to_conf_cache()

def update_soldiers_list(updater, context):
    updater.message.reply_text(text='משיג רשימת חיילים')
    report = Doch1_Report(user_config)
    res = report.login_and_get_soldiers()
    if not res[0]:
        updater.message.reply_text(text=res[1], reply_markup=reply_markup)
        return
    context.user_data['soldiers_list'] = res[1]

@restricted
def show_future_config_callback(updater, context):
    """When the command /show_future_config is issued."""
    if len(conf_cache['send_confs']) != 0 or len(conf_cache['default_configs']) != 0:
        if not 'soldiers_list' in context.user_data:
            update_soldiers_list(updater, context)

        soldiers = {}
        for soldier in context.user_data['soldiers_list']:
            soldiers[soldier['mi']] = soldier['firstName'] + ' ' + soldier['lastName']
    
    conf_cache['send_dates'].sort()
    conf_cache['send_confs'] = OrderedDict(sorted(conf_cache['send_confs'].items()))
    text='Future auto send dates:\n'
    if conf_cache['always_send']:
        text += "Always !\n"
    else:
        for date in conf_cache['send_dates']:
            text += '  {date}\n'.format(date=date.strftime('%d.%m.%Y'))

    text += '\nFuture configs:\n'    
    for date in conf_cache['send_confs'].keys():
        text += '  {date}:\n'.format(date=date.strftime('%d.%m.%Y'))
        for soldier_mi, status in conf_cache['send_confs'][date].items():
            status_code = status[0]
            note = status[1]
            text += '    {soldier_mi}: {status_code} {note}\n'.format(soldier_mi=soldiers[soldier_mi], status_code=possible_statuses[status_code][0], note=note)

    text += '\nDefault configs:\n'    
    for soldier_mi, status in conf_cache['default_configs'].items():
        status_code = status[0]
        note = status[1]
        text += '    {soldier_mi}: {status_code} {note}\n'.format(soldier_mi=soldiers[soldier_mi], status_code=possible_statuses[status_code][0], note=note)

    updater.message.reply_text(text=text)

@restricted
def send_today_report_callback(updater, context):
    """When the command /send_today_report is issued."""
    report = Doch1_Report(user_config)
    if can_send_now():
        updater.message.reply_text(text='משיג רשימת חיילים')
        res = report.login_and_get_soldiers()
        if not res[0]:
           updater.message.reply_text(text=res[1], reply_markup=reply_markup)
        context.user_data['soldiers_list'] = res[1]
        updater.message.reply_text(text='שולח')
        res = send_report(report, res[1])
        updater.message.reply_text(text='Sent report:\n{report}'.format(report=res), reply_markup=reply_markup)
    else:
        updater.message.reply_text(text='לא יכול לשלוח עכשיו, רק בין ראשון-חמישי בין השעות {start}-{end}'.format(start=START_TIME.strftime("%H:%M"), end=END_TIME.strftime("%H:%M")))
    delete_conf_cache_old_dates()
    updater.message.reply_text(text='איך תרצה להמשיך?', reply_markup=reply_markup)

def auto_send_options(updater):
    keyboard_temp = [[KeyboardButton('next morning')], [KeyboardButton('always on'), KeyboardButton('disable always on')], [KeyboardButton('X')]]
    temp_markup = ReplyKeyboardMarkup(keyboard_temp)
    updater.message.reply_text(text='באיזה תאריך? (פורמט dd.mm)', reply_markup=temp_markup)

@restricted
def toggle_auto_send_callback(updater, context):
    """When the command /toggle_auto_send is issued."""
    auto_send_options(updater)
    return DATE_SELECT

@restricted
def toggle_auto_send_by_text_callback(updater, context):
    if updater.message.text == "always on":
        conf_cache['always_send'] = True
        write_to_conf_cache()
        updater.message.reply_text(text='Auto send is now always on !', reply_markup=reply_markup)
    elif updater.message.text == "disable always on":
        conf_cache['always_send'] = False
        write_to_conf_cache()
        updater.message.reply_text(text='always on canceled !', reply_markup=reply_markup)
    elif updater.message.text == "next morning":
        updater.message.reply_text(text='Next Morning !', reply_markup=reply_markup)
        now = datetime.datetime.now()
        date = datetime.datetime.today() + datetime.timedelta(days=1)
        if now.hour < START_TIME.hour:
            date = datetime.datetime.today()
        toggle_auto_send(updater, date.date())
    else:
        updater.message.reply_text(text='da fuck do u want ?', reply_markup=reply_markup)
        auto_send_options(updater)
        return DATE_SELECT
    return ConversationHandler.END

def toggle_auto_send(updater, date):
    # Add or cancel automatic sending in specific day
    if date in conf_cache['send_dates']:
        updater.message.reply_text(text='מבטל את השליחה האוטומטית בתאריך {}'.format(date.strftime('%d.%m.%Y')))
        conf_cache['send_dates'].remove(date)
    else:
        updater.message.reply_text(text='מוסיף שליחה אוטומטית בתאריך {}'.format(date.strftime('%d.%m.%Y')))
        conf_cache['send_dates'].append(date)
    write_to_conf_cache()
    updater.message.reply_text(text='איך תרצה להמשיך?', reply_markup=reply_markup)
 
def parse_date(updater):
    try:
        # Parse date to nearest date based on day and month (round year upwards)
        date = datetime.datetime.strptime(updater.message.text, '%d.%m').replace(year=datetime.datetime.today().year)
        if date.date() < datetime.datetime.today().date(): # Change next year
            date = date.replace(year=datetime.datetime.today().year+1)
        date = date.date()
        return date
    except Exception as e:
        updater.message.reply_text(text='Can\'t parse date {}.'.format(str(e)), reply_markup=reply_markup)    
        return None

@restricted
def toggle_auto_send_by_date_callback(updater, context):
    date = parse_date(updater)
    if not date:
        auto_send_options(updater)
        return DATE_SELECT

    toggle_auto_send(updater, date)
    return ConversationHandler.END


@restricted
def change_future_config_callback(updater, context):
    """When the command /change_future_config is issued."""
    keyboard_temp = [[KeyboardButton('Next morning'), KeyboardButton('Today')], [KeyboardButton('Change default')], [KeyboardButton('X')]]
    temp_markup = ReplyKeyboardMarkup(keyboard_temp)
    updater.message.reply_text(text='באיזה תאריך? (פורמט dd.mm)', reply_markup=temp_markup)
    return DATE_SELECT      

@restricted
def change_next_morning_config_callback(updater, context):
    now = datetime.datetime.now()
    date = datetime.datetime.today() + datetime.timedelta(days=1)
    if now.hour < START_TIME.hour:
        date = datetime.datetime.today()
    context.user_data['change_future_config_date'] = date.date()

    display_people_list(updater, context)
    return PERSON_SELECT

@restricted
def change_today_config_callback(updater, context):
    now = datetime.datetime.now()
    context.user_data['change_future_config_date'] = now.date()

    display_people_list(updater, context)
    return PERSON_SELECT

@restricted
def change_default_config_callback(updater, context):
    context.user_data['change_future_config_date'] = "ALWAYS"
    display_people_list(updater, context)
    return PERSON_SELECT

@restricted
def select_future_config_date_callback(updater, context):
    date = parse_date(updater)
    if not date:
        updater.message.reply_text(text='חרא של תאריך הבאת לי', reply_markup=reply_markup)
        return ConversationHandler.END

    context.user_data['change_future_config_date'] = date
    display_people_list(updater, context)
    return PERSON_SELECT

def display_people_list(updater, context):
    # Change soldier's status in specific date
    if not 'soldiers_list' in context.user_data:
        update_soldiers_list(updater, context)

    soldiers_chunks = divide_list_to_chunks(context.user_data['soldiers_list'], round(len(context.user_data['soldiers_list'])/2))
    keyboard_temp = [[KeyboardButton(soldier['firstName']+' '+soldier['lastName']) for soldier in soldier_group] for soldier_group in soldiers_chunks]
    keyboard_temp += [[KeyboardButton('X')]]
    temp_markup = ReplyKeyboardMarkup(keyboard_temp)
    updater.message.reply_text(text='איזה חייל תרצה לשנות?', reply_markup=temp_markup)
    return PERSON_SELECT

@restricted
def soldier_name_callback(updater, context):
    """When sending soldiers name"""    

    soldier_to_change = None
    # Finding soldier by name
    for soldier in context.user_data['soldiers_list']:
        if updater.message.text == soldier['firstName']+' '+soldier['lastName']:
            soldier_to_change = soldier['mi']
    if not soldier_to_change:
        updater.message.reply_text(text='לא מצאתי את החייל..', reply_markup=reply_markup)
        return ConversationHandler.END
        
    context.user_data['change_future_config_soldier_to_change'] = soldier_to_change
    context.user_data['change_future_config_soldier_to_change_name'] = updater.message.text
    
    statuses_description = [[KeyboardButton("{status_id} - {desc}".format(status_id=status_id, desc=status_info[0]))] for status_id, status_info in possible_statuses.items()]
    statuses_description += [[KeyboardButton('X')]]

    temp_markup = ReplyKeyboardMarkup(statuses_description)
    updater.message.reply_text(text='בחר את האפשרות:\n', reply_markup=temp_markup)
    return STATUS_SELECT

@restricted
def soldier_change_status_callback(updater, context):
    """When sending status for a soldier in specific date or always"""
    status_code = updater.message.text.split("-")[0].strip().zfill(2)
    soldier_to_change = context.user_data['change_future_config_soldier_to_change']
    soldier_to_change_name = context.user_data['change_future_config_soldier_to_change_name']
    date_to_change = context.user_data['change_future_config_date']

    # If status is out of base, ask for note
    if status_code == '03':
        context.user_data['change_future_config_status_code'] = status_code
        updater.message.reply_text(text='הערה:', reply_markup=remove_markup)
        return NOTE_OUT_OF_BASE_SELECT

    return soldier_change_status(updater, context, status_code, soldier_to_change, soldier_to_change_name, date_to_change, '')

@restricted
def change_out_of_base_note_callback(updater, context):
    """When changing future status for OUT OF BASE status, with note"""
    status_code = context.user_data['change_future_config_status_code']
    soldier_to_change = context.user_data['change_future_config_soldier_to_change']
    soldier_to_change_name = context.user_data['change_future_config_soldier_to_change_name']
    date_to_change = context.user_data['change_future_config_date']

    return soldier_change_status(updater, context, status_code, soldier_to_change, soldier_to_change_name, date_to_change, updater.message.text)

def soldier_change_status(updater, context, status_code, soldier_to_change, soldier_to_change_name, date_to_change, note):
    """Save soldier's status"""
    context.user_data['change_future_config_soldier_to_change'] = None
    context.user_data['change_future_config_soldier_to_change_name'] = None
    context.user_data['change_future_config_date'] = None

    # No such status
    if not status_code in possible_statuses.keys():
        updater.message.reply_text(text='אין סטטוס כזה, נסה שנית', reply_markup=reply_markup)
        return ConversationHandler.END

    if date_to_change == "ALWAYS":
        if status_code == '01':
            if soldier_to_change in conf_cache['default_configs']:
                del conf_cache['default_configs'][soldier_to_change]
        else:
            conf_cache['default_configs'][soldier_to_change] = (status_code, note)
        updater.message.reply_text(text='שיניתי את הסטטוס הדיפולטי של {soldier} ל{status} {note}'.format(soldier=soldier_to_change_name, status=possible_statuses[status_code][0], note=note), reply_markup=reply_markup)
    else:
        # Date does not exist yet in conf_cache['send_confs']
        if not date_to_change in conf_cache['send_confs'].keys():
            conf_cache['send_confs'][date_to_change] = {}

        conf_cache['send_confs'][date_to_change][soldier_to_change] = (status_code, note)
        updater.message.reply_text(text='שיניתי בתאריך {date} את הסטטוס של {soldier} ל{status} {note}'.format(date=date_to_change, soldier=soldier_to_change_name, status=possible_statuses[status_code][0],note=note), reply_markup=reply_markup)

    write_to_conf_cache()
    return ConversationHandler.END
    
@restricted 
def cancel_callback(updater, context):
    updater.message.reply_text(text='מה תרצה לעשות?', reply_markup=reply_markup)
    return ConversationHandler.END

@restricted
def cancel_future_config_callback(updater, context):
    """When the command /cancel_future_config is issued."""
    # If nothing to cancel
    if len(conf_cache['send_confs']) == 0 and (conf_cache['always_send'] or len(conf_cache['send_dates']) == 0) and len(conf_cache['default_configs']) == 0:
        updater.message.reply_text(text="You idiot, you don't even have any future config set !", reply_markup=reply_markup)
        return ConversationHandler.END

    if not 'soldiers_list' in context.user_data:
        update_soldiers_list(updater, context)

    soldiers = {}
    for soldier in context.user_data['soldiers_list']:
        soldiers[soldier['mi']] = soldier['firstName'] + ' ' + soldier['lastName']
    
    conf_cache['send_confs'] = OrderedDict(sorted(conf_cache['send_confs'].items()))
    
    options = {}
    keyboard_temp = []
    # Generate cancel buttons for send configurations
    for date in conf_cache['send_confs'].keys():
        for soldier_mi, status in conf_cache['send_confs'][date].items():
            status_code = status[0]
            note = status[1]
            option_text = '{date} - {soldier_mi} - {status} {note}'.format(date=date.strftime('%d.%m.%Y'), soldier_mi=soldiers[soldier_mi], status=possible_statuses[status_code][0], note=note).strip()
            options[option_text] = (CANCEL_TYPE_SEND_CONFS, date, soldier_mi)
            keyboard_temp.append([KeyboardButton(option_text)])

    # Generate cancel buttons for default configurations
    for soldier_mi, status in conf_cache['default_configs'].items():
        status_code = status[0]
        note = status[1]
        option_text = 'תמיד - {soldier_mi} - {status_code} {note}'.format(soldier_mi=soldiers[soldier_mi], status_code=possible_statuses[status_code][0], note=note).strip()
        options[option_text] = (CANCEL_TYPE_DEFAULT_CONFIGS, soldier_mi)
        keyboard_temp.append([KeyboardButton(option_text)])

    # Generate cancel buttons for always send configurations (if always send is not on)
    if not conf_cache['always_send']:
        for date in conf_cache['send_dates']:
            option_text = 'שליחה בתאריך - {date}'.format(date=date.strftime('%d.%m.%Y')).strip()
            options[option_text] = (CANCEL_TYPE_SEND_DATE, date)
            keyboard_temp.append([KeyboardButton(option_text)])

    keyboard_temp.append([KeyboardButton("never mind")])
    context.user_data["cancel_options"] = options
    temp_markup = ReplyKeyboardMarkup(keyboard_temp)
    updater.message.reply_text(text="בחר את הקונפיגורציה לביטול", reply_markup=temp_markup)
    return CANCEL_SELECT

@restricted
def select_config_to_cancel_callback(updater, context):
    if updater.message.text not in context.user_data["cancel_options"].keys():
        updater.message.reply_text(text="Bad option madafaka", reply_markup=reply_markup)
        return ConversationHandler.END

    cancel_type = context.user_data["cancel_options"][updater.message.text][0]
    if cancel_type == CANCEL_TYPE_SEND_CONFS:
        _, date, soldier_mi = context.user_data["cancel_options"][updater.message.text]
        del conf_cache["send_confs"][date][soldier_mi]
        # if conf_cache['send_confs'][date_to_change] is empty, delete it from the dates list
        if len(conf_cache['send_confs'][date]) == 0:
            del conf_cache['send_confs'][date]
    elif cancel_type == CANCEL_TYPE_DEFAULT_CONFIGS:
        _, soldier_mi = context.user_data["cancel_options"][updater.message.text]
        del conf_cache["default_configs"][soldier_mi]
    elif cancel_type == CANCEL_TYPE_SEND_DATE:
        _, date = context.user_data["cancel_options"][updater.message.text]
        conf_cache["send_dates"].remove(date)

    write_to_conf_cache()
    updater.message.reply_text(text="הוסר הסטטוס {}".format(updater.message.text), reply_markup=reply_markup)
    return ConversationHandler.END


def divide_list_to_chunks(original_list, size):
    for i in range(0, len(original_list), size): 
        yield original_list[i:i + size]

 
def send_report(report, soldiers_list):
    pre_placements = {}
    default_placements = conf_cache['default_configs']
    if default_placements:
        for soldier_id, status in default_placements.items():
            pre_placements[soldier_id] = {}
            status_code = status[0]
            if status[1] != '':
                pre_placements[soldier_id]['note'] = status[1]
            pre_placements[soldier_id]['mainStatusCode'] = possible_statuses[status_code][1]
            pre_placements[soldier_id]['secondaryStatusCode'] = possible_statuses[status_code][2]

    todays_placement = conf_cache['send_confs'][datetime.datetime.today().date()] if datetime.datetime.today().date() in conf_cache['send_confs'] else None
    if todays_placement:
        for soldier_id, status in todays_placement.items():
            pre_placements[soldier_id] = {}
            status_code = status[0]
            if status[1] != '':
                pre_placements[soldier_id]['note'] = status[1]
            pre_placements[soldier_id]['mainStatusCode'] = possible_statuses[status_code][1]
            pre_placements[soldier_id]['secondaryStatusCode'] = possible_statuses[status_code][2]
    
    if pre_placements == {}:
        pre_placements = None
    return report.do_report_and_get_statuses(soldiers_list, pre_placements)


def main():
    # load user configuration file
    initialize_user_config()
    
    initialize_conf_cache()
    
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(user_config['telegram_api_key'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler('send_today', send_today_report_callback))
    dp.add_handler(CommandHandler('show_future_config', show_future_config_callback))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('toggle_auto_send', callback=toggle_auto_send_callback)],
        states={
            DATE_SELECT: [MessageHandler(Filters.regex(r'^[0-9]{1,2}\.[0-9]{1,2}$'), toggle_auto_send_by_date_callback),
                          MessageHandler(Filters.regex('X'), callback=cancel_callback),
                          MessageHandler(None, callback=toggle_auto_send_by_text_callback),
                          ],
        },
        fallbacks=[]
    ))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('change_future_config', callback=change_future_config_callback)],
        states={
            DATE_SELECT: [MessageHandler(Filters.regex(r'^[0-9]{1,2}\.[0-9]{1,2}$'), select_future_config_date_callback),
                          MessageHandler(Filters.regex(r'Change default'), change_default_config_callback),
                          MessageHandler(Filters.regex(r'Next morning'), change_next_morning_config_callback),
                          MessageHandler(Filters.regex(r'Today'), change_today_config_callback),
                          ],
            PERSON_SELECT: [MessageHandler(Filters.regex(r'^[\u0590-\u05fe\s\']+$'), soldier_name_callback)],
            STATUS_SELECT: [MessageHandler(Filters.regex(r'^[0-9]{1,2}.+$'), soldier_change_status_callback)],
            NOTE_OUT_OF_BASE_SELECT: [MessageHandler(Filters.regex(r'.*'), change_out_of_base_note_callback)],
        },              
        fallbacks=[MessageHandler(None, cancel_callback)]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('cancel_future_config', callback=cancel_future_config_callback)],
        states={
            CANCEL_SELECT: [MessageHandler(Filters.regex("never mind"), cancel_callback), MessageHandler(None, select_config_to_cancel_callback),],
        },
        fallbacks=[],
    ))

    # log all errors
    dp.add_error_handler(error)
    
    updater.bot.send_message(chat_id=user_config['telegram_chat_id'], text='מה תרצה לעשות?', reply_markup=reply_markup)

    # Start the Bot
    updater.start_polling()
    
    # start new thread for daily notifications
    args = (updater,)
    #thread.start_new_thread(setup_daily_reminder, args)
    thread.start_new_thread(setup_one_identity_routine, args)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    # Make locale understand commas is number parsing!
    # See https://stackoverflow.com/questions/2953746/python-parse-comma-separated-number-into-int.
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    main()


