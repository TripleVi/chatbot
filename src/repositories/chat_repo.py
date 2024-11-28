from datetime import datetime, timezone

from mysql.connector import Error as MySQLError

from src.config.database import get_db_connection

async def get_chat(id: int):
    try:
        cnx = await get_db_connection()
        cur = await cnx.cursor(dictionary=True)
        query = "SELECT * FROM chat WHERE id = %s"
        await cur.execute(query, (id,))
        return await cur.fetchone()
    finally:
        await cur.close()
        await cnx.close()

async def add_chat(user_id, title) -> int:
    try:
        cnx = await get_db_connection()
        cur = await cnx.cursor(dictionary=True)
        query = """
            INSERT INTO chat (user_id, title, created_at)
            VALUES (%s, %s, %s)
        """
        data = (user_id, title, datetime.now(timezone.utc))
        await cur.execute(query, data)
        await cnx.commit()
        return cur.lastrowid
    except MySQLError:
        await cnx.rollback()
        raise
    finally:
        await cur.close()
        await cnx.close()

async def get_chat_history(id: int) -> tuple[str | None, tuple[dict]]:
    try:
        cnx = await get_db_connection()
        cur = await cnx.cursor(dictionary=True)
        get_chat = "SELECT summary, summary_id FROM chat WHERE id = %s"
        await cur.execute(get_chat, (id,))
        chat = await cur.fetchone()
        get_messages = """
            SELECT id, content FROM message
            WHERE chat_id = %s AND id > %s
            ORDER BY id ASC
        """
        await cur.execute(get_messages, (id, chat["summary_id"]))
        messages = await cur.fetchall()
        return (chat["summary"], messages)
    finally:
        await cur.close()
        await cnx.close()

async def add_message(message: tuple):
    try:
        cnx = await get_db_connection()
        cur = await cnx.cursor(dictionary=True)
        query = """
            INSERT INTO message (content, sender, chat_id, created_at)
            VALUES (%s, %s, %s, %s)
        """
        data = message + (datetime.now(timezone.utc),)
        await cur.execute(query, data)
        await cnx.commit()
        return {
            "id": cur.lastrowid,
            "created_at": data[-1].isoformat(),
        }
    except MySQLError:
        await cnx.rollback()
        raise
    finally:
        await cur.close()
        await cnx.close()

async def update_message(id, content):
    try:
        cnx = await get_db_connection()
        cur = await cnx.cursor(dictionary=True)
        query = """
            UPDATE message
            SET content = %s
            WHERE id = %s
        """
        await cur.execute(query, (content, id))
        await cnx.commit()
    except MySQLError:
        await cnx.rollback()
        raise
    finally:
        await cur.close()
        await cnx.close()

async def update_summary(id: int, summary: str, summary_id: int):
    try:
        cnx = await get_db_connection()
        cur = await cnx.cursor(dictionary=True)
        query = """
            UPDATE chat
            SET summary = %s, summary_id = %s
            WHERE id = %s
        """
        await cur.execute(query, (summary, summary_id, id))
        await cnx.commit()
    except MySQLError:
        await cnx.rollback()
        raise
    finally:
        await cur.close()
        await cnx.close()
