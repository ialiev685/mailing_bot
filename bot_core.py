import telebot
from config import API_TOKEN, BOT_SENDER_ORDER_TOKEN


if API_TOKEN:
    bot = telebot.TeleBot(API_TOKEN)

if BOT_SENDER_ORDER_TOKEN:
    bot_sender = telebot.TeleBot(BOT_SENDER_ORDER_TOKEN)
