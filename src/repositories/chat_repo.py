from datetime import datetime, timezone

from mysql.connector import Error as MySQLError

from src.config.database import get_db_connection

def get_chat(id: int):
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        query = "SELECT * FROM chat WHERE id = %s"
        cur.execute(query, (id,))
        return cur.fetchone()
    finally:
        cur.close()
        cnx.close()

def add_chat(user_id, title) -> int:
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        query = """
            INSERT INTO chat (user_id, title, created_at)
            VALUES (%s, %s, %s)
        """
        now = datetime.now(timezone.utc)
        cur.execute(query, (user_id, title, now))
        cnx.commit()
        return cur.lastrowid
    except MySQLError:
        cnx.rollback()
        raise
    finally:
        cur.close()
        cnx.close()

def get_chat_history(id: int) -> tuple[str | None, tuple[dict]]:
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        get_chat = "SELECT summary, summary_id FROM chat WHERE id = %s"
        cur.execute(get_chat, (id,))
        chat = cur.fetchone()
        get_messages = """
            SELECT content FROM message
            WHERE chat_id = %s AND id > %s
            ORDER BY id ASC
        """
        cur.execute(get_messages, (id, chat["summary_id"]))
        messages = cur.fetchall()
        return (chat["summary"], messages)
    finally:
        cur.close()
        cnx.close()

def add_message(content, sender, chat_id) -> int:
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)

        query = """
            INSERT INTO message (content, sender, chat_id, created_at)
            VALUES (%s, %s, %s, %s)
        """
        now = datetime.now(timezone.utc)
        cur.execute(query, (content, sender, chat_id, now))
        cnx.commit()
        return cur.lastrowid
    except MySQLError:
        cnx.rollback()
        raise
    finally:
        cur.close()
        cnx.close()
