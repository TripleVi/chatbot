from config.database import get_db_connection

def get_project(id: int, attributes: list):
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        select_list = ", ".join(attributes) if attributes else "*"
        query = f"SELECT {select_list} FROM project WHERE id = %s"
        cur.execute(query, (id,))
        return cur.fetchone()
    finally:
        cur.close()
        cnx.close()

def get_authors(project_id: int, attributes: list):
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        select_list = ", ".join(attributes) if attributes else "*"
        query = f"SELECT {select_list} FROM author WHERE project_id = %s"
        cur.execute(query, (project_id,))
        return cur.fetchall()
    finally:
        cur.close()
        cnx.close()
