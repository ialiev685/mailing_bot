import telebot
from dotenv import load_dotenv
import os

load_dotenv(".env")

API_TOKEN = os.getenv("BOT_TOKEN", None)

bot = telebot.TeleBot(API_TOKEN)
