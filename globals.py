import asyncio
import sqlite3
from config.config import Config
from loguru import logger
from aiogram import Bot
from db_models.User import engine, all_users_table, data_users_table

#-_-_-_-_-CONNECTS-_-_-_-_-
try:
    config = Config() #Config load
    logger.info("[+] True loaded configuration")
except Exception as e:
    logger.exception(e)

try:
    bot = Bot(token = config.token) #connect t0 Telegram API
    logger.info("[+] True connect to Telegram API")
except Exception as e:
    logger.exception(e)

conn = engine.connect()
#-_-_-_-_-_-END-_-_-_-_-_-

#-_-_-_-_-VARIABLES -_-_-_-_-
bot_info:dict = None #Bot information
seconds:int = 0      #Counter variable
my_class = None
now_process:bool = True #Process T/F
count_mailing:int = 0
#-_-_-_-_-_-END-_-_-_-_-_-

#-_-_-_-_-KEYBOARDS-_-_-_-_-
keyboards:list = [
    ["⚠️Статистика COVID-19"], 
    ["💣Атаковать номер"],
    ["🌐Изменить язык"], 
    ["✉️Написать сообщение"]
]
#-_-_-_-_-_-END-_-_-_-_-_-