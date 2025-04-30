import telebot
API = "7617476622:AAEoLxt-87bFhL-gpeL4-mJDn1M-LIjzEWw"
bot = telebot.TeleBot(API)


def send_notification(user_id, mssg):
    bot.send_message(user_id, mssg)