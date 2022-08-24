# http://t.me/SmallSales_bot
# pip install pytelegrambotapi

import telebot
from telebot import types
import requests

SERVER_PATH = 'http://192.168.0.10:8880'
bot = telebot.TeleBot('token', parse_mode='HTML')

markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn_POST = types.KeyboardButton('Внести')
btn_GET = types.KeyboardButton('Получить')
markup.row(btn_POST, btn_GET)

@bot.message_handler(commands=['start'])
def send_welcome(message):
   bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
   
   
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
   if message.text == "Внести":
      # bot.send_message(message.chat.id, "Ввод новой записи.")
      post_1(message.chat.id)
   elif message.text == "Получить":
      # bot.send_message(message.chat.id, "Получение данных.")
      get_1(message.chat.id)
   else:
      send_welcome(message)


def post_1(chat_id):
   msg = bot.send_message(chat_id,
         'Введите дату в формате DD.MM.YYYY:')
   bot.register_next_step_handler(msg, post_2)


def post_2(message):
   if check_restart(message) == 1:
      return
   
   # check input data here
   if len(message.text) != 10:
      bot.send_message(message.chat.id, 'Некорректный формат.')
      post_1(message.chat.id)
      return
      
   bot.send_message(message.chat.id, 'Введите объём:')
   bot.register_next_step_handler(message, post_3, message.text)


def post_3(message, date_value):
   if check_restart(message) == 1:
      return

   # check input data here
   tmp_num = message.text.replace(',','.')
   if not is_number(tmp_num):
      bot.send_message(message.chat.id, 'Некорректный формат.')
      message.text=date_value
      post_2(message)
      return
   
   r_post = req_post(tmp_num, date_value)
   r_post.do_request(message)
   bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    
    
def get_1(chat_id):
   msg = bot.send_message(chat_id,
         'Введите <b>дату начала</b> в формате DD.MM.YYYY:')
   bot.register_next_step_handler(msg, get_2)
   
def get_2(message):
   if check_restart(message) == 1:
      return
   
   # check input data here
   if len(message.text) != 10:
      bot.send_message(message.chat.id, 'Некорректный формат.')
      get_1(message.chat.id)
      return
      
   bot.send_message(message.chat.id, 'Введите <b>дату окончания</b> в формате DD.MM.YYYY:')
   bot.register_next_step_handler(message, get_3, message.text)


def get_3(message, date_value):
   if check_restart(message) == 1:
      return

   # check input data here
   if len(message.text) != 10:
      bot.send_message(message.chat.id, 'Некорректный формат.')
      message.text=date_value
      get_2(message)
      return
      
   r_get = req_get(date_value, message.text)
   r_get.do_request(message)
   bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


def check_restart(message):
   if message.text == "Получить" or message.text == "Внести":
      get_text_messages(message)
      return 1
   else:
      return 0


def is_number(check_str):
    try:
        float(check_str)
        return True
    except ValueError:
        return False

   
class req_post:
   def __init__(self, volume, date):
      self.volume = volume
      self.date = date
   
   def do_request(self, message):
      r_params = {'volume': self.volume, 'date': self.date}
      try:
         response = requests.post(f'{SERVER_PATH}', params=r_params)
         bot.send_message(message.chat.id, response.text)
      except Exception as e:
         bot.send_message(message.chat.id, "Ошибка запроса: " + str(e))
         

class req_get:
   def __init__(self, datefrom, dateto):
      self.datefrom = datefrom
      self.dateto = dateto
   
   def do_request(self, message):
      r_params = {'datefrom': self.datefrom, 'dateto': self.dateto}
      try:
         response = requests.get(f'{SERVER_PATH}', params=r_params)
         # response.encoding = 'utf-8'
         bot.send_message(message.chat.id, response.text)
      except Exception as e:
         bot.send_message(message.chat.id, "Ошибка запроса: " + str(e))

        
bot.infinity_polling()