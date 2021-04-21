import asyncio
#from globals import Bot, cursor
from aiogram.types import Message
from globals import config, conn, all_users_table, data_users_table
from sqlalchemy import select

async def statistics(msg: Message):
    if msg.from_user.id in config.admins:

        all_ids_all_users = select([all_users_table.c.user_id])
        all_ids_all_users = conn.execute(all_ids_all_users).fetchall()

        data_all_ids_users = select([data_users_table.c.user_id])
        data_all_ids_users = conn.execute(data_all_ids_users).fetchall()
        
        endless_status = select([data_users_table.c.status]).where(data_users_table.c.status=="∞")
        endless_status = conn.execute(endless_status).fetchall()

        await msg.answer(
            f"📊Статистика:\n"
            f"Общее количество: {len(all_ids_all_users)}\n"
            f"Активировали бомбер: {len(data_all_ids_users)}\n"
            f"Приоритетный статус (∞): {len(endless_status)}"
        )