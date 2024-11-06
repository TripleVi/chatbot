import os
from datetime import datetime, timezone

import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_DATABASE"]
    )

def get_chat(id: int):
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        get_chat = "SELECT * FROM chat WHERE id = %s"
        cur.execute(get_chat, (id,))
        chat = cur.fetchone()
        return chat
    finally:
        cur.close()
        cnx.close()

def get_messages(chat_id: int):
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        get_messages = "SELECT * FROM message WHERE chat_id = %s"
        cur.execute(get_messages, (chat_id,))
        messages = cur.fetchall()
        return messages
    finally:
        cur.close()
        cnx.close()

def get_message(id: int):
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        get_message = "SELECT * FROM message WHERE id = %s"
        cur.execute(get_message, (id,))
        message = cur.fetchone()
        return message
    finally:
        cur.close()
        cnx.close()

def add_message(*, content, sender, chat_id) -> int:
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)

        add_message = """
            INSERT INTO message (content, sender, chat_id, created_at)
            VALUES (%s, %s, %s, %s)
        """
        now = datetime.now(timezone.utc)
        data_message = (content, sender, chat_id, now)
        cur.execute(add_message, data_message)
        cnx.commit()
        return cur.lastrowid
    finally:
        cur.close()
        cnx.close()

def add_chat(*, user_id, title) -> int:
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        add_chat = """
            INSERT INTO chat (user_id, title, created_at)
            VALUES (%s, %s, %s)
        """
        now = datetime.now(timezone.utc)
        data_chat = (user_id, title, now)
        cur.execute(add_chat, data_chat)
        cnx.commit()
        return cur.lastrowid
    finally:
        cur.close()
        cnx.close()

def get_project(id: int):
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        get_project = "SELECT * FROM project WHERE id = %s"
        cur.execute(get_project, (id,))
        project = cur.fetchone()
        return project
    finally:
        cur.close()
        cnx.close()