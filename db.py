import os

import psycopg2

from settings import DATABASE


class ClosingConnection:
    def __init__(self, schema_name: str) -> None:
        """
        :param schema_name: the db schema (i.e. the tenant)
        """
        super().__init__()
        self.schema_name = schema_name

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(
                host=os.environ["DB_HOST"],
                port=os.environ["DB_PORT"],
                database=os.environ["DB_NAME"],
                user=os.environ["DB_USERNAME"],
                password=password,
                options=f"-c search_path={self.schema_name}",
                cursor_factory=psycopg2.extras.DictCursor,
            )
            return self.conn
        except psycopg2.OperationalError:
            pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


def get_db(schema_name: str):
    return ClosingConnection(schema_name)


with get_db("test") as db:
    with db.cursor() as cursor:
        cursor.execute("some sql")
        rv = cursor.fetchall()


class Cursor:
    def __init__(self,
                 host=DATABASE.get('HOST'),
                 user=DATABASE.get('USER'),
                 password=DATABASE.get('PASSWORD'),
                 db_name=DATABASE.get('NAME'),
                 driver=connector,
                 ):
        self.driver = driver
        self.connection = self.driver.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, ext_type, exc_value, traceback):
        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()
