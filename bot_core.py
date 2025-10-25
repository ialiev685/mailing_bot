import telebot
from dotenv import load_dotenv
from config import API_TOKEN, BOT_SENDER_ORDER_TOKEN

load_dotenv(".env")

if API_TOKEN:
    bot = telebot.TeleBot(API_TOKEN)

if BOT_SENDER_ORDER_TOKEN:
    bot_sender = telebot.TeleBot(BOT_SENDER_ORDER_TOKEN)
