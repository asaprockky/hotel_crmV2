import telebot
API = "7795647781:AAEzf1va_osHyZxHhhZIg9wuWI7S-Jf-Ftk"
bot = telebot.TeleBot(API)


def send_notification(user_id, mssg):
    bot.send_message(user_id, mssg)