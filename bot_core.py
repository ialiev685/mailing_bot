import telebot
from dotenv import load_dotenv
import os
from config import API_TOKEN

load_dotenv(".env")

if API_TOKEN:
    bot = telebot.TeleBot(API_TOKEN)
