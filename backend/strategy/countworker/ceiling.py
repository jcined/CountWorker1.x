import sqlite3
import aiohttp
import asyncio

# 发送请求
async def send_request_loop(path: str, message: dict, live_id) -> None:
    url = f'http://127.0.0.1:10010{path}?id={live_id}'
    data = {'message': message}
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=data)


def send_request(path: str, message: dict, live_id) -> None:
    asyncio.run(send_request_loop(path=path, message=message, live_id=live_id))


def insertLog(time: int, type: str, info: str, live_id):
    db = SQLiteOperator(live_id)
    db.insert_data("logs", "time, type, info", f"'{str(time)}', '{str(type)}', '{str(info)}'")
    db.close()


# sqlite操作
class SQLiteOperator:
    def __init__(self, live_id):
        db_name = f"./strategy/Lives/{live_id}/data/strategy.db"
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name}({columns})")
        self.conn.commit()

    def insert_data(self, table_name, columns, values):
        self.cursor.execute(f"INSERT INTO {table_name}({columns}) VALUES({values})")
        self.conn.commit()

    def select_data(self, table_name, columns="*", condition=""):
        self.cursor.execute(f"SELECT {columns} FROM {table_name} {condition}")
        return self.cursor.fetchall()

    def update_data(self, table_name, set_values, condition=""):
        self.cursor.execute(f"UPDATE {table_name} SET {set_values} {condition}")
        self.conn.commit()

    def delete_data(self, table_name, condition=""):
        self.cursor.execute(f"DELETE FROM {table_name} {condition}")
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
