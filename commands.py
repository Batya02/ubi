import os 
import json
import asyncio
import sqlite3
import globals
import requests
from loguru import logger
from bs4 import BeautifulSoup
from aiogram import types
from aiogram.utils import executor
from datetime import datetime as dt
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import (
                            ReplyKeyboardRemove, ReplyKeyboardMarkup, 
                            KeyboardButton, InlineKeyboardMarkup, 
                            InlineKeyboardButton
                          )

from db_models.User import all_users_table, data_users_table
from sqlalchemy import select

class Userstate(StatesGroup):
    attack_phone = State()          #Функция для атаки номера
    send_messages = State()         #Функция для отправки рассылки        
    user_id = State()               #ID пользователя
    send_message = State()          #Функция для отправки сообщения
    select_language = State()       #Функция для выбора языка
    try_try = State()               #Функция исключения
    send_message_func1 = State()    #Функция для отправки сообщения _1
    send_message_func2 = State()    #Функция для отправки сообщения _2
    id_user_var = State()           #ID юзера

@logger.catch
async def own_start(message: types.Message):
    '''
    Функция записывает нового пользователя, если он отсутсвует в базе. 
    Если пользователь присутствует в базе, 
    тогда бот отправляет основные команды.
    '''

    my_data = select([all_users_table]).where(all_users_table.c.user_id==message.from_user.id)
    my_data = globals.conn.execute(my_data).fetchall()

    if my_data == []:

        date_reg = dt.strftime(dt.now(), "%d-%m-%Y %H:%M:%S:")

        user_id = message.from_user.id
        username = str(message.from_user.username)

        insert_data = all_users_table.insert().values(
            user_id=message.from_user.id, 
            username=message.from_user.username, 
            date_registration=date_reg, 
            language="None"
        )

        globals.conn.execute(insert_data)

        '''
        await globals.bot.send_message(globals.config.chat_id, 
                            text="🆕New user!\n"+\
                            f"ID: {str(message.from_user.id)}\n"+\
                            f"@{str(message.from_user.username)}")
        '''

        lang_usl = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🇬🇧ENG", callback_data="ENG")],
                [InlineKeyboardButton(text="🇷🇺RU", callback_data="RU")]
            ])

        await globals.bot.send_message(message.chat.id, 
                            text="🌐Select the language\n"+\
                                 "🌐Выберите язык",
                            reply_markup=lang_usl)
    else:
        language = my_data[0][3]

        if language == "None":
            lang_usl = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🇬🇧ENG", callback_data="ENG")], 
                    [InlineKeyboardButton(text="🇷🇺RU", callback_data="RU")]
                ]
            )

            await globals.bot.send_message(message.chat.id, 
                    text=f"🌐Select the language\n"
                    f"🌐Выберите язык",
                    reply_markup=lang_usl
            )
        
        elif language == "ENG":
            globals.lang = "ENG"
            await eng_start(message)

        elif language == "RU":
            globals.lang = "RU"
            await ru_start(message)

@logger.catch
async def ru_start(message: types.Message):
    '''
    Функция отправляет основные команды для рускоязычных пользователей.
    Вызывается в условии в own_start()
    '''
    usl = ReplyKeyboardMarkup(
        keyboard = [
            #["🔔Участвовать в конкурсе"],
            ["⚠️Статистика COVID-19"], 
            ["💣Атаковать номер"],
            ["🌐Изменить язык"], 
            ["✉️Написать сообщение"]
        ], 
        resize_keyboard = True
    )
    await globals.bot.send_message(message.chat.id, 
            text="🤖Universal Bot\n\nВыберите действие👇🏼", 
            reply_markup = usl)

@logger.catch
async def eng_start(message: types.Message):
    '''
    Функция отправляет основные команды для англоязычных пользователей.
    Вызывается в условии в own_start()
    '''
    usl = ReplyKeyboardMarkup(
        keyboard = [
            ["⚠️COVID-19 statistics"], 
            ["💸Currency"], 
            ["💣Attack number"], 
            ["🌐Change the language"], 
            ["✉️Send message"]
        ], 
        resize_keyboard = True
    )
    await globals.bot.send_message(message.chat.id, 
                           text="🤖Universal Bot\n\nSelect an action👇🏼", 
                           reply_markup = usl)

@logger.catch
async def ru_covid_19(message: types.Message):
    '''
    Функция парсит информацию с интернет-ресурса и отправляет в бот.
    Статистика о Covid-19 для рускоязычных пользователей.
    '''

    r = requests.get(url="https://xn--80aesfpebagmfblc0a.xn--p1ai/")
    html = r.text
    soup = BeautifulSoup(html, "lxml")
    line1 = soup.find_all("div", class_ = "cv-countdown__item-value")
    date  = dt.strftime(dt.now(), "Дата: *%d-%m-%Y* - Время: *%H:%M:%S*")

    await globals.bot.send_message(
                message.chat.id, 
                text=str(date)+" - Страна: *Россия*\n\n"+\
                f"1️⃣ Проведено тестов: *{line1[0].text}*\n"
                f"2️⃣ Случаев заболевания: *{line1[1].text}*\n"
                f"3️⃣ Случаев заболевания за последние сутки: *{line1[2].text}*\n"
                f"4️⃣ Человек выздоровело: *{line1[3].text}*\n"
                f"5️⃣ Человека умерло: *{line1[4].text}*", 
                parse_mode = "Markdown")

@logger.catch
async def eng_covid_19(message: types.Message):
    '''
    Функция парсит информацию с интернет-ресурса и отправляет в бот.
    Статистика о Covid-19 для англоязычных пользователей.
    '''

    r = requests.get(url="https://xn--80aesfpebagmfblc0a.xn--p1ai/")
    html = r.text
    soup = BeautifulSoup(html, "lxml")
    line1 = soup.find_all("div", class_ = "cv-countdown__item-value")
    await globals.bot.send_message(
                message.chat.id, 
                text=dt.strftime(dt.now(), 
                        "Date: *%d-%m-%Y* - Time: *%H:%M:%S*")+" - Country: *Russia*\n\n"
                f"1️⃣ Tests performed: *{line1[0].text[:-4]}mln*\n"
                f"2️⃣ Disease cases: *{line1[1].text}*\n"
                f"3️⃣ Disease cases in the last 24 hours: *{line1[2].text}*\n"
                f"4️⃣ Man recovered: *{line1[3].text}*\n"
                f"5️⃣ The person died: *{line1[4].text}*", 
                parse_mode = "Markdown")

@logger.catch
async def ru_currency(message: types.Message):
    '''
    Функция парсит информацию о валюте с разных 
    интернет-ресурсов.
    '''
       
    r = requests.get(url="https://www.yandex.ru") #Yandex url
    soup = BeautifulSoup(r.text, "html.parser")   #HTML-page

    #Get Dollar currency
    dollar = soup.find("div", class_ = "b-inline inline-stocks__item "+
    "inline-stocks__item_id_2002 hint__item inline-stocks__part")
    dollar = dollar.find("span", class_ = "inline-stocks__value_inner")

    #Get Euro currency
    euro = soup.find("div",  class_ = "b-inline inline-stocks__item "+
    "inline-stocks__item_id_2000 hint__item inline-stocks__part")
    euro = euro.find('span', class_ = 'inline-stocks__value_inner')

    #Get Oil currency
    oil = soup.find("div", class_ = "b-inline inline-stocks__item "+
    "inline-stocks__item_id_1006 hint__item")
    oil = oil.find("span", class_ = "inline-stocks__value_inner")

    #Get Bitcoin currency
    url_btc = requests.get(timeout=1, url=
    "https://www.banknn.ru/kurs-kriptovalyut/bitcoin")
    btc_soup = BeautifulSoup(url_btc.text, "html.parser")
    btc = btc_soup.find("td", class_ = "digit")

    #Get Ethereum currency
    url_eth = requests.get(timeout=1, url=
    "https://www.banknn.ru/kurs-kriptovalyut/ethereum")
    eth_soup = BeautifulSoup(url_eth.text, "html.parser")
    eth = eth_soup.find("td", class_ = "digit")

    #Get Ripple(xrp) currency
    url_xrp = requests.get(timeout=1, url=
    "https://www.banknn.ru/kurs-kriptovalyut/ripple")
    xrp_soup = BeautifulSoup(url_xrp.text, "html.parser")
    xrp = xrp_soup.find("td", class_ = "digit")

    #Get BNB(Binance) currency
    url_bnb = requests.get(timeout=1, url=
    "https://www.binance.com/en/trade/BNB_BUSD")
    bnb_soup = str(BeautifulSoup(url_bnb.text, "html.parser").find(id="__APP_DATA"))
    bnb = json.loads(bnb_soup.replace("</script>", "").replace('<script id="__APP_DATA" type="application/json">', ""))
    bnb = bnb["pageData"]["redux"]["products"]["currentProduct"]["close"]
    try:
        await globals.bot.send_message(message.chat.id,
        text=f"💵Доллар: *"+str(dollar.text)+"*\n"
        f"💶Евро: *{euro.text}*\n"
        f"🛢Нефть: *{oil.text}*\n\n"
        f"💎Криптовалюта:\n"
        f"BTC: `{btc.text}$`\n"
        f"ETH: `{eth.text}$`\n"
        f"XRP: `{xrp.text}$`\n"
        f"BNB: `{bnb}$`",
        parse_mode = "Markdown")
    except Exception as e:
        logger.error(e)
        await globals.bot.send_message(message.chat.id, 
        text=f"💵Доллар: *{dollar.text}*\n"
        f"💶Евро: *{euro.text}*\n"
        f"🛢Нефть: *{oil.text}*\n\n"
        f"💎Криптовалюта:\n"
        f"BTC: `{btc.text}$`\n"
        f"ETH: `{eth.text}$`\n"
        f"XRP: `{xrp.text}$`", 
        parse_mode = "Markdown")

@logger.catch
async def eng_currency(message: types.Message):
    '''
    Функция парсит информацию о валюте с разных 
    интернет-ресурсов.
    '''
    
    r = requests.get(timeout=1, url="https://www.yandex.ru") #Yandex url
    soup = BeautifulSoup(r.text, "lxml")                     #HTML-page

    #Get Dollar currency
    dollar = soup.find("div",    class_ = "b-inline inline-stocks__item "+ 
    "inline-stocks__item_id_2002 hint__item inline-stocks__part")
    dollar = dollar.find("span", class_ = "inline-stocks__value_inner")

    #Get Euro currency
    euro = soup.find("div",  class_ = "b-inline inline-stocks__item "+
    "inline-stocks__item_id_2000 hint__item inline-stocks__part")
    euro = euro.find('span', class_ = 'inline-stocks__value_inner')

    #Get Oil currency
    oil = soup.find("div", class_ = "b-inline inline-stocks__item "+
    "inline-stocks__item_id_1006 hint__item")
    oil = oil.find("span", class_ = "inline-stocks__value_inner")

    #Get Bitcoin currency
    url_btc = requests.get(timeout=1, 
    url="https://www.banknn.ru/kurs-kriptovalyut/bitcoin")
    btc_soup = BeautifulSoup(url_btc.text, "lxml")
    btc = btc_soup.find("td", class_ = "digit")

    #Get Ethereum currency
    url_eth = requests.get(timeout=1, 
    url="https://www.banknn.ru/kurs-kriptovalyut/ethereum")
    eth_soup = BeautifulSoup(url_eth.text, "lxml")
    eth = eth_soup.find("td", class_ = "digit")

    #Get Xrp currency
    url_xrp = requests.get(timeout=1, 
    url="https://www.banknn.ru/kurs-kriptovalyut/ripple")
    xrp_soup = BeautifulSoup(url_xrp.text, "lxml")
    xrp = xrp_soup.find("td", class_ = "digit")

    #Get BNB currency
    url_bnb = requests.get(timeout=1, 
    url="https://coinmarketcap.com/ru/currencies/binance-coin")
    bnb_soup = BeautifulSoup(url_bnb.text, "lxml")
    bnb = bnb_soup.find("span", class_ = "cmc-details-panel-price__price")

    try:
        await globals.bot.send_message(message.chat.id, 
        text=f"💵Dollar: *{dollar.text}*\n"
        f"💶Euro: *{euro.text}*\n"
        f"🛢OIL: *{oil.text}*\n\n"
        f"💎Cryptocurrency:\n"
        f"BTC: `{btc.text}$`\n"
        f"ETH: `{eth.text}$`\n"
        f"XRP: `{xrp.text}$`\n"
        f"BNB: `{bnb.text[1:]}$`", 
        parse_mode = "Markdown")
    except:
        await globals.bot.send_message(message.chat.id, 
        text=f"💵Dollar: *{dollar.text}*\n"
        f"💶Euro: *{euro.text}*\n"
        f"🛢OIL: *{oil.text}*\n\n"
        f"💎Cryptocurrency:\n"
        f"BTC: `{btc.text}$`\n"
        f"ETH: `{eth.text}$`\n"
        f"XRP: `{xrp.text}$`", 
        parse_mode = "Markdown")

@logger.catch
async def get_currency_usd(message: types.Message):
    '''
    Функция получает последнюю инфомарцию о валюте(Доллар)

    '''
    try:
        await globals.bot.delete_message(message.chat.id, message.message_id)
    except:await globals.bot.delete_message(message.from_user.id, message.message_id)

    try:
        usd_url = requests.get(timeout=0.5, url=
        "https://www.binance.com/en/trade/USDT_RUB")
        usd_soup = str(BeautifulSoup(usd_url.text, "html.parser").find(id="__APP_DATA"))
        usd = json.loads(usd_soup.replace("</script>", "").replace('<script id="__APP_DATA" type="application/json">', ""))
        usd = usd["pageData"]["redux"]["products"]["currentProduct"]

        symbol = usd["symbol"]
        close_price = usd["close"]
        low_price = usd["low"]
        high_price = usd["high"]

        await globals.bot.send_message(
            message.chat.id, 
            text=f"*{symbol}*\n"
            f"_Now_: `{close_price}`\n"
            f"_Min_: *{low_price}*\n"
            f"_Max_: *{high_price}*", 
            parse_mode="Markdown"
        )
    except Exception as e:
        await globals.bot.send_message(
            message.chat.id, 
            text=f"⚠️Ошибка при отправке запроса...\n"
            f"Информация об ошибке ➔ {e}"
        )

@logger.catch
async def get_currency_btc(message: types.Message):
    '''
    Функция получает последнюю инфомарцию о валюте(Биткоин)
    '''

    try:
        await globals.bot.delete_message(message.chat.id, message.message_id)
    except:await globals.bot.delete_message(message.from_user.id, message.message_id)

    try:
        btc_url = requests.get(timeout=0.5, url=
        "https://www.binance.com/en/trade/BTC_USDT")
        btc_soup = str(BeautifulSoup(btc_url.text, "html.parser").find(id="__APP_DATA"))
        btc = json.loads(btc_soup.replace("</script>", "").replace('<script id="__APP_DATA" type="application/json">', ""))
        btc = btc["pageData"]["redux"]["products"]["currentProduct"]

        symbol = btc["symbol"]
        close_price = btc["close"]
        low_price = btc["low"]
        high_price = btc["high"]

        await globals.bot.send_message(
            message.chat.id, 
            text=f"*{symbol}*\n"
            f"_Now_: `{close_price}`\n"
            f"_Min_: *{low_price}*\n"
            f"_Max_: *{high_price}*", 
            parse_mode="Markdown"
        )
    except Exception as e:
        await globals.bot.send_message(
            message.chat.id, 
            text=f"⚠️Ошибка при отправке запроса...\n"
            f"Информация об ошибке ➔ {e}"
        )

@logger.catch
async def get_currency_eth(message: types.Message):
    '''
    Функция получает последнюю инфомарцию о валюте(Эфир)
    '''

    try:
        await globals.bot.delete_message(message.chat.id, message.message_id)
    except:await globals.bot.delete_message(message.from_user.id, message.message_id)

    try:
        eth_url = requests.get(timeout=0.5, url=
        "https://www.binance.com/en/trade/ETH_USDT")
        eth_soup = str(BeautifulSoup(eth_url.text, "html.parser").find(id="__APP_DATA"))
        eth = json.loads(eth_soup.replace("</script>", "").replace('<script id="__APP_DATA" type="application/json">', ""))
        eth = eth["pageData"]["redux"]["products"]["currentProduct"]

        symbol = eth["symbol"]
        close_price = eth["close"]
        low_price = eth["low"]
        high_price = eth["high"]

        await globals.bot.send_message(
            message.chat.id, 
            text=f"*{symbol}*\n"
            f"_Now_: `{close_price}`\n"
            f"_Min_: *{low_price}*\n"
            f"_Max_: *{high_price}*", 
            parse_mode="Markdown"
        )
    except Exception as e:
        await globals.bot.send_message(
            message.chat.id, 
            text=f"⚠️Ошибка при отправке запроса...\n"
            f"Информация об ошибке ➔ {e}"
        )

@logger.catch
async def get_currency_bnb(message: types.Message):
    '''
    Функция получает последнюю инфомарцию о валюте(Доллар)
    '''

    try:
        await globals.bot.delete_message(message.chat.id, message.message_id)
    except:await globals.bot.delete_message(message.from_user.id, message.message_id)
    
    try:
        bnb_url = requests.get(timeout=0.5, url=
        "https://www.binance.com/en/trade/BNB_USDT")
        bnb_soup = str(BeautifulSoup(bnb_url.text, "html.parser").find(id="__APP_DATA"))
        bnb = json.loads(bnb_soup.replace("</script>", "").replace('<script id="__APP_DATA" type="application/json">', ""))
        bnb = bnb["pageData"]["redux"]["products"]["currentProduct"]

        symbol = bnb["symbol"]
        close_price = bnb["close"]
        low_price = bnb["low"]
        high_price = bnb["high"]

        await globals.bot.send_message(
            message.chat.id, 
            text=f"*{symbol}*\n"
            f"_Now_: `{close_price}`\n"
            f"_Min_: *{low_price}*\n"
            f"_Max_: *{high_price}*", 
            parse_mode="Markdown"
        )
    except Exception as e:
        await globals.bot.send_message(
            message.chat.id, 
            text=f"⚠️Ошибка при отправке запроса...\n"
            f"Информация об ошибке ➔ {e}"
        )

@logger.catch
async def adm(message: types.Message):
    '''
    Админ-панель
    1. Рассылка
    2. Отправка сообщения по ID пользователя
    '''

    if str(message.from_user.id) == str(globals.config.chat_id):
        usl = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text = "📣Рассылка", 
                                    callback_data = "Рассылка")],
                [InlineKeyboardButton(text = "📧Отправить сообщение(ID)", 
                                    callback_data= "Отправить сообщение(ID)")]
            ]
        )

        await globals.bot.send_message(message.chat.id, 
                               text="🤖Universal Bot\n\nВыберите действие👇🏼", 
                               reply_markup = usl)
        await Userstate.try_try.set()
    else:pass

@logger.catch
async def ru_send_message(message: types.Message):
    '''
    Отправка сообщения владельцу.
    Рускоязычные пользователи.
    '''

    await globals.bot.send_message(message.chat.id, 
    f"🔑Мы полностью заботимся о конфиденциальности пользователя, "
    f"поэтому интегрировали функцию отправки сообщения через бота!\n\n "
    f"Напишите сообщение:")
    await Userstate.send_message.set()

@logger.catch
async def eng_send_message(message: types.Message):
    '''
    Отправка сообщения владельцу.
    Англоязычные пользователи.
    '''

    await globals.bot.send_message(message.chat.id,
    f"🔑We completely care about user privacy, "
    f"so we integrated the function of sending a message through a bot!\n\n "
    f"Write a message:")
    await Userstate.send_message.set()

@logger.catch
async def change_language(message:types.Message):
    '''
    Функция изменения языка
    Дается выбор: 
        1. Английский(ENG)
        2. Русский(RUS)
    '''

    change_language_usl = InlineKeyboardMarkup(
        inline_keyboard = [
            [InlineKeyboardButton(text="🇬🇧ENG", callback_data="ENG")],
            [InlineKeyboardButton(text="🇷🇺RU", callback_data="RU")]
        ]
    )

    await globals.bot.send_message(message.chat.id, 
                           text = f"🌐Select the language\n"
                                  f"🌐Выберите язык", 
    reply_markup=change_language_usl)

@logger.catch
async def ru_attack_phone(message: types.Message):
    '''
    Функция, выводящую информацию при нажатии на кнопку "Атаковать"

    Основные данные:
        1. Дата и время
        2. Номер телефона
        3. Количество кругов

    Рускоязычные пользователи.
    '''

    user_id = message.from_user.id

    my_data = select([data_users_table]).where(data_users_table.c.user_id==user_id)
    my_data = globals.conn.execute(my_data).fetchone()

    if my_data == None:

        date = dt.strftime(dt.now(), "%d-%m-%Y %H:%M:%S")

        update_data = data_users_table.insert().values(
            user_id=user_id, 
            date=date, 
            status=30, 
            last_phone="None", 
            last_date="None"
        )
        globals.conn.execute(update_data)

        await globals.bot.send_message(
            user_id, 
            text=f"✅Вы зарегестрированы! Вам доступно 30 кругов."
            f"Нажмите еще раз на кнопку 💣Атаковать номер"
        )

    else:

        download_program = InlineKeyboardMarkup(
            inline_keyboard=[
                    [InlineKeyboardButton(text="⬇️Загрузить программу", 
                                    callback_data="Загрузить программу")], 
                    [InlineKeyboardButton(text="❔Информация о программе", 
                                    callback_data="Информация о программе")]
            ]
        )

        try:
            date  = dt.strptime(my_data[4], "%d-%m-%Y %H:%M:%S")
            date  = dt.strftime(date, "*Дата: %d-%m-%Y* *Время: %H:%M:%S*")                      
        except:date = "Круги неизвестны!"
        
        if my_data[2] == "∞":

            if my_data[3] == "None" and my_data[4] == "None":

                await globals.bot.send_message(user_id, 
                f"📄Информация о последней атаки ➜\n\n"
                f"📌Вы еще не совершали атаку!\n\n"
                f"☎️Введите номер телефона жертвы (79#########):", 
                reply_markup=download_program)
                await Userstate.attack_phone.set()

            else:

                await globals.bot.send_message(user_id, 
                f"📄Информация о последней атаки ➜\n\n"
                f"📅🕰{date}\n"
                f"📌Номер: `{my_data[3]}`\n"
                f"⏱Осталось кругов: *{my_data[2]}*\n\n"
                f"☎️Введите номер телефона жертвы (79#########):", 
                reply_markup=download_program, parse_mode = "Markdown")
                await Userstate.attack_phone.set()

        else:

            if int(my_data[2]) == 0:

                await globals.bot.send_message(user_id, 
                f"📄Информация о последней атаки ➜\n\n📅🕰{date}\n"
                f"📌Номер: `{my_data[3]}`\n"
                f"⌛Статус: *Круги исчерпаны!*", 
                reply_markup=download_program, parse_mode = "Markdown") 
                await Userstate.try_try.set()   

            else:

                if my_data[3] == "None" and my_data[4] == "None":
                    await globals.bot.send_message(user_id, 
                    f"📄Информация о последней атаки ➜\n\n"
                    f"📌Вы еще не совершали атаку!\n\n"
                    f"☎️Введите номер телефона жертвы (79#########):", 
                    reply_markup=download_program)
                    await Userstate.attack_phone.set()
                
                else:

                    date = dt.strptime(my_data[4], "%d-%m-%Y %H:%M:%S")
                    date = dt.strftime(date, "*%d-%m-%Y* *%H:%M:%S*")

                    await globals.bot.send_message(user_id, 
                    f"📄Информация о последней атаки ➜\n\n"
                    f"📅🕰{date}\n📌Номер: `{my_data[3]}`\n"
                    f"⏱Осталось кругов: *{my_data[2]}*\n\n"
                    "☎️Введите номер телефона жертвы (79#########):", 
                    reply_markup=download_program, parse_mode = "Markdown")
                    await Userstate.attack_phone.set()

@logger.catch
async def eng_attack_phone(message: types.Message):
    '''
    Функция, выводящую информацию при нажатии на кнопку "Атаковать"

    Основные данные:
        1. Дата и время
        2. Номер телефона
        3. Количество кругов

    Англоязычные пользователи.
    '''
    #State user_id
    user_id = message.from_user.id

    my_data = select([data_users_table]).where(data_users_table.c.user_id==user_id)
    my_data = globals.conn.execute(my_data).fetchone()

    if my_data == None:

        date = dt.strftime(dt.now(), "%d-%m-%Y %H:%M:%S")

        update_data = data_users_table.insert().values(
            user_id=user_id, 
            date=date, 
            status=30, 
            last_phone="None", 
            last_date="None"
        )
        globals.conn.execute(update_data)

        await globals.bot.send_message(
            user_id, 
            text=f"✅You are registered! You have 30 laps available."
            f"Click again on the button 💣Attack number"
        )

    else:
        download_program = InlineKeyboardMarkup(
            inline_keyboard=[
                    [InlineKeyboardButton(text="⬇️Download the program", 
                                    callback_data="Download the program")], 
                    [InlineKeyboardButton(text="❔Info about the program", 
                                    callback_data="Info about the program")]
            ]
        )

        try:
            date = dt.strptime(my_data[4], "%d-%m-%Y %H:%M:%S")
            date = dt.strftime(date, "*Date: %d-%m-%Y* *Time: %H:%M:%S*")

        except: date = "Time unknown!"

        if str(my_data[2]) == "∞":

            if my_data[3] == "None" and my_data[4] == "None":

                await globals.bot.send_message(user_id, 
                f"📄Information about the last attack ➜\n\n"
                f"📌You haven't made an attack yet!\n\n"
                f"☎️Enter the victim's phone number (79#########):", 
                reply_markup=download_program)
                await Userstate.attack_phone.set()

            else:

                date = dt.strptime(my_data[4], "%d-%m-%Y %H:%M:%S")
                date = dt.strftime(date, "Date: *%d-%m-%Y* Time: *%H:%M:%S*")
                
                await globals.bot.send_message(user_id, 
                f"📄Information about the last attack ➜\n\n"
                f"📅🕰{date}\n📌Phone number: `{my_data[3]}`\n"
                f"⏱Circles left: *{my_data[2]}*\n\n"
                "Enter the victim's phone number (79#########):", 
                reply_markup=download_program, parse_mode = "Markdown")
                await Userstate.attack_phone.set()
        else:

            if int(my_data[2]) == 0:
                await globals.bot.send_message(user_id, 
                f"📄Information about the last attack ➜\n\n"
                f"📅🕰{date}\n📌Phone number: `{my_data[3]}`\n"
                "⌛Status: *The circles are gone!*", 
                reply_markup=download_program, parse_mode = "Markdown") 
                await Userstate.try_try.set()  

            else:

                if my_data[3] == "None" and my_data[4] == "None":
                    await globals.bot.send_message(user_id, 
                    f"📄Information about the last attack ➜\n\n"
                    f"📌You haven't made an attack yet!\n\n"
                    f"☎️Enter the victim's phone number (79#########):", 
                    reply_markup=download_program)
                    await Userstate.attack_phone.set()
                
                else:
                    await globals.bot.send_message(user_id, 
                    f"📄Information about the last attack ➜\n\n"
                    f"📅🕰{date}\n📌Phone number: `{my_data[3]}`\n"
                    f"⏱Circles left: *{my_data[2]}*\n\n"
                    "☎️Enter the victim's phone number (79#########):", 
                    reply_markup=download_program, parse_mode = "Markdown")
                    await Userstate.attack_phone.set()

@logger.catch
async def subscribe_concurs(message: types.Message):
    '''
    Проведение конкурса
    '''

    _my_data = open("referals_data.json", "r")
    my_data = json.loads(_my_data.read())
    if str(message.from_user.id) in my_data:
        usl = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❓Статус конкурса", 
                                      callback_data="❓Статус конкурса")]
            ]
        )
        await globals.bot.send_message(message.chat.id, 
        f"🕒Вы участвуете в конкурсе.\n\n"
        f"👥Количество приглашенных пользователей:\
        {len(my_data[str(message.from_user.id)])}\n"
        f"📃Условия конкурса: Пригласить большое количество пользователей,\
         опередить своих конкурентов!\n"+
        f"💰Приз: 500₽\n\n"+
        f"🔗Ваша реферальная ссылка:\
        https://t.me/{globals.bot_info.username}/?start={str(message.from_user.id)}", 
        reply_markup=usl)
        _my_data.close()
    else: 
        my_data[str(message.from_user.id)] = []
        with open("referals_data.json", "w") as f:
            f.write(json.dumps(my_data))
            f.close()
        await globals.bot.send_message(message.chat.id, 
        f"💥Поздравляю, Вы записаны на конкурс. Спасибо за участие!\n\n"+
        f"👥Количество приглашенных пользователей:\
        {len(my_data[str(message.from_user.id)])}\n"+
        f"📃Условия конкурса: Пригласить большое количество пользователей,\
         опередить своих конкурентов!\n"+
        f"💰Приз: 500₽\n\n"+
        f"🔗Ваша реферальная ссылка:\
         https://t.me/{globals.bot_info.username}/?start={str(message.from_user.id)}")
        _my_data.close()

@logger.catch
async def help(message: types.Message) -> str:
    language = select([all_users_table]).where(all_users_table.c.user_id==message.from_user.id)
    language = globals.conn.execute(language).fetchone()

    if language[3] == "ENG":
        
        with open(r"_data/help_eng.txt", "r", encoding="utf-8") as help_text_read:
            help_text = help_text_read.read()

    elif language[3] == "RU":

        with open(r"_data/help_ru.txt", "r", encoding="utf-8") as help_text_read:
            help_text = help_text_read.read()
    
    return await message.reply(help_text, parse_mode="Markdown")