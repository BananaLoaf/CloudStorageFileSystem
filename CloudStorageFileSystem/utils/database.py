import sqlite3
import threading
from typing import List, Tuple, Optional, Union
from functools import wraps
import time

from pathlib import Path


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


class DatabaseItem:
    headers = {}
    not_required = []

    def __init__(self):
        self._data = {}

    @classmethod
    def from_list(cls, row: Union[list, tuple]):
        data = {}
        for i, name in enumerate(cls.headers.keys()):
            data[name] = row[i]

        obj = cls()
        obj._data = data
        return obj

    @classmethod
    def from_kwargs(cls, **kwargs):
        self = cls()

        for key in self.headers.keys():
            if key not in kwargs.keys() and key not in self.not_required:
                raise KeyError(key)
            elif key not in self.not_required:
                self._data[key] = kwargs[key]

        return self

    @property
    def tuple(self) -> tuple:
        l = []
        for key in self.headers.keys():
            l.append(self[key])
        return tuple(l)

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return str(self._data)


def eval_kwargs(cls: DatabaseItem):
    def decorator(func):
        @wraps(func)
        def wrapped(self, **kwargs):
            for key in kwargs.keys():
                assert key in cls.headers.keys(), f"Invalid key '{key}' in kwargs"

            return func(self, **kwargs)

        return wrapped
    return decorator


class Database:
    def __init__(self, filename: Path):
        self.conn = sqlite3.connect(str(filename), check_same_thread=False)
        self.lock = threading.Lock()

    def create_table(self, name: str, headers: dict, reset: bool = False):
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