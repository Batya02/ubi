import asyncio
import commands
from _commands import statistics
import globals

async def repeat_commands(commands):
    username = await globals.bot.get_me()
    return {
        "/start":commands.own_start,
        "/help":commands.help,
        "/usd":commands.get_currency_usd,
        f"/usd@{username.username}":commands.get_currency_usd, 
        "/btc":commands.get_currency_btc,
        f"/btc@{username.username}":commands.get_currency_btc,
        "/eth":commands.get_currency_eth,
        f"/eth@{username.username}":commands.get_currency_eth,  
        "/bnb":commands.get_currency_bnb,
        f"/bnb@{username.username}":commands.get_currency_bnb,
        "⚠️Статистика COVID-19":commands.ru_covid_19,
        "💣Атаковать номер":commands.ru_attack_phone,
        "/adm":commands.adm,
        "/stat":statistics.statistics,
        "✉️Написать сообщение":commands.ru_send_message,
        "🌐Изменить язык":commands.change_language,
        "⚠️COVID-19 statistics":commands.eng_covid_19,
        "💸Currency":commands.eng_currency,
        "💣Attack number":commands.eng_attack_phone,
        "🌐Change the language":commands.change_language, 
        "✉️Send message":commands.eng_send_message 
    }

