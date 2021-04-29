import os 
import re
import json
import asyncio
import sqlite3
from loguru import logger
from aiohttp import ClientSession
from datetime import datetime as dt

import commands
import globals
from sites import Bomber
from config.config import Config
from repeat_commands import repeat_commands
from _commands.statistics import statistics

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ( Message,
                            ReplyKeyboardMarkup, KeyboardButton, 
                            InlineKeyboardMarkup, InlineKeyboardButton
                          )

from db_models.User import all_users_table, data_users_table
from sqlalchemy import select

logger.add("debug.log", format="{time} {level} {message}", 
    level="DEBUG", rotation="1 week", compression="zip")

storage = MemoryStorage()
loop = asyncio.get_event_loop()
dp = Dispatcher(globals.bot, storage=storage, loop=loop)

send_mess_PATH = os.getcwd()  #Основной путь к файлам бота

class Userstate(StatesGroup):
    attack_phone = State()          #Функция для атаки номера
    send_messages = State()         #Функция для отправки рассылки        
    user_id = State()               #ID пользователя
    send_message = State()          #Функция для отправки сообщения
    try_try = State()               #Функция исключения
    send_message_func1 = State()    #Функция для отправки сообщения _1
    send_message_func2 = State()    #Функция для отправки сообщения _2
    id_user_var = State()           #ID юзера

#Own functions ----------> ###################################################
@dp.message_handler(content_types = ["text"])
async def own(message: types.Message, state:FSMContext):
    await state.update_data(user_id = str(message.from_user.id))
    globals.message = message

    globals.rep_comm = await repeat_commands(commands)

    if message.text in list(globals.rep_comm):
        await globals.rep_comm[message.text](message)
    else:pass

#Attack phone nomber ----------> #############################################
@dp.message_handler(state = Userstate.attack_phone)
async def attack_phone(message: types.Message, state: FSMContext):
    '''
    Функция принимает ввод от пользователя.
    Ввод мобильного.
    '''

    if message.text in list(globals.rep_comm):
        await globals.rep_comm[message.text](message)
    else:
        phone = re.sub("[^0-9]", "", message.text)

        if phone.startswith("7") or phone.startswith("8"):
            phone = f"7{phone[1:]}"
            globals.attack_country = "ru"

        elif phone.startswith("38"):
            globals.attack_country = "uk"
        
        else:
            return await message.answer("🔁Не удалось определить страну. Проверьте номер на корректность!", reply=True)

        date = dt.strftime(dt.now(), "%d-%m-%Y %H:%M:%S")

        update_data = data_users_table.update().values(
            last_phone=message.text,
            last_date=date
        ).where(data_users_table.c.user_id==message.from_user.id)
        globals.conn.execute(update_data)

        usl = InlineKeyboardMarkup(
            inline_keyboard = [
                [InlineKeyboardButton("⏹Остановить", 
                callback_data="Остановить")]
            ])

        await message.answer(
        text="▶️Атака началась!\nНажмите кнопку для остановки атаки.", 
        reply_markup = usl)
        try:
            globals.my_class = Bomber(user_id=str(message.from_user.id))
            await globals.my_class.start(message.text, message.from_user.id)
        except:pass

#Admin mailing ----------> ###################################################           
@dp.message_handler(state = Userstate.send_messages, 
                    content_types = ["text", "photo"])
async def send_messages(message: types.Message, state: FSMContext):
    '''
    Функция рассылки.
    Принимает сообщения от админа.
    '''

    all_users = select([all_users_table.c.user_id])
    all_users = globals.conn.execute(all_users).fetchall()

    if message.text in list(globals.rep_comm):
        await globals.rep_comm[message.text](message)
    else:

        start_time = dt.utcnow()

        half_lists = int(len(all_users)/2)
        part_1 = all_users[:half_lists]
        part_2 = all_users[half_lists:]

        part_3 = part_1[int(len(part_1)/2):]
        part_1 = part_1[:int(len(part_1)/2)]

        part_4 = part_2[int(len(part_2)/2):]
        part_2 = part_2[:int(len(part_2)/2)]

        if message.photo:
            #Если контент - фото
            photo = await globals.bot.get_file(
            message.photo[len(message.photo) - 1].file_id)
            photo = await globals.bot.download_file(photo.file_path)

            for user_1 in part_1:
                globals.count_mailing+=1
                try:
                    await globals.bot.send_message(user_1[0], message.text)
                except:pass
            
            for user_2 in part_2:
                globals.count_mailing+=1
                try:
                    await globals.bot.send_message(user_2[0], message.text)
                except:pass
            
            for user_3 in part_3:
                globals.count_mailing+=1
                try:
                    await globals.bot.send_message(user_3[0], message.text)
                except:pass
            
            for user_4 in part_4:
                globals.count_mailing+=1
                try:
                    await globals.bot.send_message(user_4[0], message.text)
                except:pass

        elif message.text:        
            #Если контент - текст

            for user_1 in part_1:
                globals.count_mailing+=1
                try:
                    await globals.bot.send_message(user_1[0], message.text)
                except:pass
            
            for user_2 in part_2:
                globals.count_mailing+=1
                try:
                    await globals.bot.send_message(user_2[0], message.text)
                except:pass
            
            for user_3 in part_3:
                globals.count_mailing+=1
                try:
                    await globals.bot.send_message(user_3[0], message.text)
                except:pass
            
            for user_4 in part_4:
                globals.count_mailing+=1
                try:
                    await globals.bot.send_message(user_4[0], message.text)
                except:pass

        end_time = (dt.utcnow() - start_time).total_seconds()
        await message.answer(
                f"✅Рассылка завершена! (Count: {globals.count_mailing})\n"+\
                "⏱Время(sec): {:.2f}".format(end_time), 
                reply=True)

        globals.count_mailing = 0
        
        await Userstate.try_try.set()

@dp.message_handler(state = Userstate.send_message)
async def send_message(message: types.Message, state:FSMContext):
    '''
    Функция отправляет сообщения админу.
    '''

    if message.text in list(globals.rep_comm):
        await globals.rep_comm[message.text](message)
    else:
        language = select([all_users_table.c.language]).where(all_users_table.c.user_id==message.from_user.id)
        language = globals.conn.execute(language).fetchone()
       
        if language[0] == "None":
            lang_usl = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🇬🇧ENG", 
                                                callback_data="ENG")], 
                    [InlineKeyboardButton(text="🇷🇺RU", 
                                                callback_data="RU")]
                ]
            )

            await globals.bot.send_message(message.chat.id, 
                    text="🌐Select the language\n"+\
                         "🌐Выберите язык",
                    reply_markup=lang_usl)

        else:
            #Отправка сообщения админу
            await globals.bot.send_message(globals.config.chat_id, 
                    text = f"User ID: <code>{str(message.from_user.id)}</code>\n"
                           f"Username: @{str(message.from_user.username)}\n"
                           f"Message: {message.text}", parse_mode="HTML")

            if language[0] == "ENG":
                #Сообщение об успешной отправке(ENG)
                await globals.bot.send_message(message.chat.id, 
                        text="✅Message sent successfully!")

            elif language[0] == "RU":
                #Сообщение об успешной отправке(RU)
                await globals.bot.send_message(message.chat.id, 
                        text="✅Сообщение успешно отправлено!")
                    
        await Userstate.try_try.set()

@dp.message_handler(state=Userstate.try_try)
async def try_try(message: types.Message, state:FSMContext):
    '''
    Функция обрабатывает исключения
    '''

    if message.text in list(globals.rep_comm):
        await globals.rep_comm[message.text](message)
    else:pass

@dp.message_handler(state=Userstate.send_message_func1)
async def send_message1(message: types.Message, state:FSMContext):
    '''
    Функция получает сообщение от админа для отправки сообщения 
    пользователю.
    '''

    if message.text in list(globals.rep_comm):
        await globals.rep_comm[message.text](message)
    else:
        if not message.text.isdigit():
            await globals.bot.send_message(message.chat.id, 
                    text="❗️ID должно содержать только цифры!")
            await Userstate.send_message_func1.set()
        else:
            await state.update_data(id_user_var=str(message.text))
            await globals.bot.send_message(message.chat.id, 
                    text="📧Введите сообщение:")
            await Userstate.send_message_func2.set()

@dp.message_handler(state=Userstate.send_message_func2)
async def send_message2(message: types.Message, state:FSMContext):
    '''
    Функция позволяет отправлять сообщения пользователю 
    от админа бота.
    '''

    if message.text in list(globals.rep_comm):
        await globals.rep_comm[message.text](message)
    else:
        data = await state.get_data()
        _id = data.get("id_user_var")
        try:
            await globals.bot.send_message(int(_id), message.text)
            await globals.bot.send_message(message.chat.id, 
                    text="✅Сообщение успешно отправлено!")
        except:await globals.bot.send_message(message.chat.id, 
            text="👁Неправильный ID или пользователь заблокировал бота!")
        await Userstate.try_try.set()

#CALLBACK ----------> ########################################################
@dp.callback_query_handler(lambda call: True, state="*")
async def knopki(call: types.CallbackQuery, state: FSMContext):

    data = await state.get_data()
    userID = data.get("user_id")
    language = select([all_users_table.c.language]).where(all_users_table.c.user_id==userID)
    language = globals.conn.execute(language).fetchone()[0]

    if call.data == "Остановить":

        if language == "ENG": message = "✔️Attack stopped!"
        else: message = "✔️Атака остановлена!"
        try:
            await globals.my_class.stop(str(userID))
            await globals.bot.edit_message_text(
                            chat_id = call.message.chat.id, 
                            message_id = call.message.message_id, 
                            text =  message)
        except UnboundLocalError:
            await globals.my_class.stop(str(userID))
            await globals.bot.edit_message_text(
                            chat_id = call.message.chat.id, 
                            message_id = call.message.message_id, 
                            text =  message)
    
    elif call.data == "Рассылка":
        usl = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text = "📧Сообщение", 
                                      callback_data = "Сообщение")], 
                [InlineKeyboardButton(text = "🖼Изображение", 
                                      callback_data = "Изображение")]
            ])
        await globals.bot.edit_message_text(chat_id = call.message.chat.id, 
                                    message_id = call.message.message_id, 
        text = "Выберите пункт👇🏼", reply_markup = usl)
        await Userstate.try_try.set()

    elif call.data == "Сообщение":
        await globals.bot.edit_message_text(chat_id = call.message.chat.id, 
                                       message_id = call.message.message_id, 
        text = "📝Напишите сообщение:")
        await Userstate.send_messages.set()

    elif call.data == "Изображение":
        await globals.bot.edit_message_text(chat_id = call.message.chat.id, 
                                       message_id = call.message.message_id, 
        text = "🖼Прикрепите изображние ➜")
        await Userstate.send_messages.set()

    elif call.data == "ENG":
        update_data = all_users_table.update().values(
            language="ENG"
        ).where(all_users_table.c.user_id==userID)
        globals.conn.execute(update_data)

        await globals.bot.edit_message_text(chat_id = call.message.chat.id, 
                                       message_id = call.message.message_id, 
                                       text = "🌐Russian ➜ English")
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
        await globals.bot.send_message(call.message.chat.id, 
                               text="🤖Universal Bot\n\nSelect an action👇🏼", 
                               reply_markup = usl)
    
    elif call.data == "RU":

        update_language = all_users_table.update().values(language="RU")
        globals.conn.execute(update_language)

        await globals.bot.edit_message_text(chat_id = call.message.chat.id, 
                                    message_id = call.message.message_id, 
                                    text = "🌐Английский ➜ Русский")
        usl = ReplyKeyboardMarkup(
        keyboard = [
            #["🔔Участвовать в конкурсе"],
            ["⚠️Статистика COVID-19"], 
            ["💣Атаковать номер"],
            ["🌐Изменить язык"], 
            ["✉️Написать сообщение"]], 
        resize_keyboard = True)
        await globals.bot.send_message(call.message.chat.id, 
                               text="🤖Universal Bot\n\nВыберите действие👇🏼", 
                               reply_markup = usl)

    elif call.data == "Отправить сообщение(ID)":
        await globals.bot.edit_message_text(chat_id = call.message.chat.id, 
                                    message_id = call.message.message_id, 
                                    text = "👁‍🗨Введите ID пользователя:")
        await Userstate.send_message_func1.set()

    elif call.data == "Загрузить программу":
        filename = os.listdir("program")
        for program in filename:
            formats_program = program.split(".")
            formats_program.reverse()
            if formats_program[0] == "exe":
                crator_program = open(r"program/%s" % program, "rb")
        
                await globals.bot.edit_message_text(
                        chat_id = call.message.chat.id, 
                        message_id = call.message.message_id, 
                        text = "🔄Дождитесь загрузки...")

                await globals.bot.send_chat_action(
                call.message.chat.id, 'typing')
                await globals.bot.send_document(
                call.message.chat.id, crator_program)
                await globals.bot.send_message(call.message.chat.id, 
                                        text="✅Загрузка завершена!")
            else:pass

    elif call.data == "Информация о программе":
        if not os.path.exists("program"):
            os.mkdir("program")
            await globals.bot.send_message(globals.config.chat_id, 
            text="Directory created but not exists files!")
            await globals.bot.edit_message_text(
                    chat_id = call.message.chat.id, 
                    message_id = call.message.message_id, 
                    text = "⚠️Отсутствуют файлы!"
            )
        else:
            dir_program = os.listdir("program")
            if dir_program == []:
                await globals.bot.edit_message_text(
                        chat_id = call.message.chat.id, 
                        message_id = call.message.message_id, 
                        text = "⚠️Отсутствуют файлы!"
                )
            else:
                for program_info in dir_program:
                    program = program_info.split(".")
                    program.reverse()
                    if program[0] == "jpg":
                        program_photo = open(r"program/%s" % program_info, "rb")
                        program_photo = program_photo.read()
                        await globals.bot.delete_message(
                        call.message.chat.id, call.message.message_id)
                        await globals.bot.send_photo(
                        call.message.chat.id, program_photo, 
                        caption=f"💣Crater Bomber\n\n"
                        f"📃Программа от Universal Bot\n"
                        f"🖥В случае падения бота, можно запустить "
                        f"программу на платформе Windows (на компьютере).\n"
                        f"➕Из плюсов: бесконечные секунды!\n"
                        f"⚙️Программа будет получать дальнейшие " 
                        f"обновления и радовать Вас!")
                    else:pass           

    elif call.data == "Download the program":
        filename = os.listdir("program")
        for program in filename:
            formats_program = program.split(".")
            formats_program.reverse()
            if formats_program[0] == "exe":
                crator_program = open(r"program/%s" % program, "rb")
                await globals.bot.edit_message_text(
                        chat_id = call.message.chat.id, 
                        message_id = call.message.message_id, 
                        text = "🔄Wait for loading..."
                )
                await globals.bot.send_chat_action(
                    call.message.chat.id, 'typing'
                )
                await globals.bot.send_document(
                    call.message.chat.id, crator_program
                )
                await globals.bot.send_message(call.message.chat.id, 
                                            text="✅Download done!")

    elif call.data == "Info about the program":
        if not os.path.exists("program"):
            os.mkdir("program")
            await globals.bot.send_message(globals.config.chat_id, 
            text="Directory created but not exists files!")
            await globals.bot.edit_message_text(
                    chat_id = call.message.chat.id, 
                    message_id = call.message.message_id, 
                    text = "⚠️Files missing!"
            )
        else:
            dir_program = os.listdir("program")
            if dir_program == []:
                await globals.bot.edit_message_text(
                        chat_id = call.message.chat.id, 
                        message_id = call.message.message_id, 
                        text = "⚠️Files missing!"
                )
            else:
                for program_info in dir_program:
                    program = program_info.split(".")
                    program.reverse()
                    if program[0] == "jpg":
                        program_photo = open(r"program/%s" + program_info, "rb")
                        program_photo = program_photo.read()
                        await globals.bot.delete_message(
                        call.message.chat.id, call.message.message_id)
                        await globals.bot.send_photo(
                        call.message.chat.id, program_photo, 
                        caption=f"💣Crater Bomber\n\n"
                        f"📃Program from Universal Bot\n"
                        f"🖥If the bot crashes, you can run "
                        f"the program on the Windows "
                        f"platform (on a computer).\n"
                        f"➕Of the pluses: endless seconds!\n"
                        f"⚙️The program will receive further "
                        f"updates and delight you!")
                    else:pass

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)