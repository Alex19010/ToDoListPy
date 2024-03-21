from bot import BOT as bot
from handlers import *

if __name__ == "__main__":
    print("Бот запущен")
    manager.create_table()
    bot.infinity_polling()