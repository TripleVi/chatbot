import os

from mysql.connector.aio import connect

def get_db_connection():
    return connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_SCHEMA"]
    )
