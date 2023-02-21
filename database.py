import sqlite3
import asyncio
import pandas as pd
from pandas import ExcelWriter

conn = ''
cursor = ''


async def connection_database():
    try:
        global conn, cursor
        conn = sqlite3.connect('data\\database.db')
        cursor = conn.cursor()

    except BaseException:
        return BaseException


async def insert_telegram_info(values):
    global conn, cursor
    query = f'insert into telegram_info ("name", "date_request") values (?, ?)'
    cursor.execute(query, values)
    conn.commit()
    return cursor.lastrowid


async def insert_user(name, class_u, number, t_id, spec):
    global conn, cursor
    query = f'insert into user (name, number, class, telegram_info_id, speciality) values (?, ?, ?, ?, ?)'
    cursor.execute(query, [name, number, class_u, t_id, spec])
    conn.commit()  


async def sql_to_excel():
    global conn, cursor
    await connection_database()

    query_user = "select * from user"
    query_telegram_info = "select * from telegram_info"
    
    dataframe_user = pd.read_sql_query(query_user, conn)
    dataframe_telegram_info = pd.read_sql_query(query_telegram_info, conn)

    dataframe_user.to_excel('data\\user.xlsx', sheet_name="user")
    dataframe_telegram_info.to_excel('data\\telegram_info.xlsx', sheet_name="telegram_info")