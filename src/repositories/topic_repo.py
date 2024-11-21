from config.database import get_db_connection

def get_topic(id: int, attributes: list):
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        select_list = ", ".join(attributes) if attributes else "*"
        query = f"SELECT {select_list} FROM topic WHERE id = %s"
        cur.execute(query, (id,))
        return cur.fetchone()
    finally:
        cur.close()
        cnx.close()
