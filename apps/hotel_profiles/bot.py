import telebot
API = "5963235436:AAESz8DiZYjKaGJD0vxPP1hv2CEcWOjlPQk"
bot = telebot.TeleBot(API)


def send_notification(user_id, mssg):
    bot.send_message(user_id, mssg)