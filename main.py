import logging

from bot_core import bot
from handlers.mailing import *
from handlers.order import *


def init_logger_config():
    logging.basicConfig(
        filename="logs.log",
        level=logging.INFO,
        format="%(asctime)s - %(filename)s - row:%(lineno)s - %(levelname)s - %(message)s - callback name:%(func_name)s",
    )


if __name__ == "__main__":
    while True:
        try:

            init_logger_config()
            bot.infinity_polling(restart_on_change=True)
            # bot.infinity_polling()

        except Exception as error:
            print("error by start server:", error)
