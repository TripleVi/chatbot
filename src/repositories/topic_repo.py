from config.database import get_db_connection

async def get_topic(id: int, attributes: list):
    try:
        cnx = await get_db_connection()
        cur = await cnx.cursor(dictionary=True)
        select_list = ", ".join(attributes) if attributes else "*"
        query = f"SELECT {select_list} FROM topic WHERE id = %s"
        await cur.execute(query, (id,))
        return await cur.fetchone()
    finally:
        await cur.close()
        await cnx.close()
