from config.database import get_db_connection

async def get_project(id: int, attributes: list):
    try:
        cnx = await get_db_connection()
        cur = await cnx.cursor(dictionary=True)
        select_list = ", ".join(attributes) if attributes else "*"
        query = f"SELECT {select_list} FROM project WHERE id = %s"
        await cur.execute(query, (id,))
        return await cur.fetchone()
    finally:
        await cur.close()
        await cnx.close()

async def get_authors(project_id: int, attributes: list):
    try:
        cnx = await get_db_connection()
        cur = await cnx.cursor(dictionary=True)
        select_list = ", ".join(attributes) if attributes else "*"
        query = f"SELECT {select_list} FROM author WHERE project_id = %s"
        await cur.execute(query, (project_id,))
        return await cur.fetchall()
    finally:
        await cur.close()
        await cnx.close()
