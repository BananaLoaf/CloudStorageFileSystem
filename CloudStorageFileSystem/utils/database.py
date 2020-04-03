import sqlite3
import threading
from typing import List, Tuple, Optional, Union
from functools import wraps
import time


def lock(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        self.lock.acquire()
        try:
            res = func(self, *args, **kwargs)
        except:
            raise
        finally:
            self.lock.release()

        return res
    return wrapped


def handle_exceptions(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except sqlite3.OperationalError as err:
            print(err)
            time.sleep(1)
            return wrapped(self, *args, **kwargs)
    return wrapped


class Database:
    def __init__(self, filename: str):
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.lock = threading.Lock()

    def create_table(self, name: str, headers: dict, reset: bool = True):
        if reset:
            self.conn.execute(f"DROP TABLE IF EXISTS '{name}'")
        columns = ", ".join([f"'{key}' {headers[key]}" for key in headers.keys()])
        self.conn.execute(f"CREATE TABLE IF NOT EXISTS '{name}' ({columns})")

    @lock
    @handle_exceptions
    def _execute_fetchone(self, query: str, values: List) -> Tuple:
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        return cursor.fetchone()

    @lock
    @handle_exceptions
    def _execute_fetchall(self, query: str, values: Optional[List] = None) -> List[Tuple]:
        args = [query]
        if values is not None:
            args.append(values)

        cursor = self.conn.cursor()
        cursor.execute(*args)
        return cursor.fetchall()

    @lock
    @handle_exceptions
    def _execute(self, query: str, values: Optional[Union[List, Tuple]] = None):
        args = [query]
        if values is not None:
            args.append(values)

        cursor = self.conn.cursor()
        cursor.execute(*args)
        self.conn.commit()

    @lock
    @handle_exceptions
    def _executemany(self, query: str, values: List):
        args = [query, values]

        cursor = self.conn.cursor()
        cursor.executemany(*args)
        self.conn.commit()