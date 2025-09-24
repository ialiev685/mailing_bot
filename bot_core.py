import telebot
from dotenv import load_dotenv
import os
from config import API_TOKEN

load_dotenv(".env")


bot = telebot.TeleBot(API_TOKEN)
