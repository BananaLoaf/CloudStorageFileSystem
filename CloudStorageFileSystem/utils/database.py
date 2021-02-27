import sqlite3
import threading
from typing import *
from functools import wraps
import time

from pathlib import Path


ROWID = "rowid"


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
    _columns = {}
    _ignored_keys = [ROWID]
    _not_required = []  # For defaults

    def __init__(self):
        self._data = {}

    @classmethod
    def from_list(cls, row: Union[list, tuple]):
        self = cls()

        for i, name in enumerate(self.headers):
            self._data[name] = row[i]

        return self

    @classmethod
    def from_kwargs(cls, **kwargs):
        self = cls()

        for header in self.headers:
            # If header is not in kwargs and IS required
            if header not in kwargs.keys() and header not in self._not_required:
                raise KeyError(header)
            else:
                self._data[header] = kwargs[header]

        return self

    @property
    def headers(self) -> tuple:
        return tuple(self._columns.keys())

    @property
    def values(self) -> tuple:
        return tuple(self._data.values())

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return str(self._data)


def eval_kwargs(cls: Type[DatabaseItem]):
    def decorator(func):
        @wraps(func)
        def wrapped(self, **kwargs):
            for key in kwargs.keys():
                # Ignore existence of some keys
                if key in cls._ignored_keys:
                    continue

                # Scream if some key is extra
                assert key in cls._columns.keys(), f"Invalid key '{key}' in kwargs"

            return func(self, **kwargs)

        return wrapped
    return decorator


class Database:
    def __init__(self, filename: Path):
        self.conn = sqlite3.connect(str(filename), check_same_thread=False)
        self.lock = threading.Lock()

    def drop_table(self, name: str):
        self._execute(f"DROP TABLE IF EXISTS '{name}'")

    def create_table(self, name: str, headers: dict, reset: bool = False):
        if reset:
            self.drop_table(name)
        columns = ", ".join([f"'{key}' {headers[key]}" for key in headers.keys()])
        self._execute(f"CREATE TABLE IF NOT EXISTS '{name}' ({columns})")

    def create_index(self, table_name: str, column_name: str):
        self._execute(f"CREATE INDEX IF NOT EXISTS {column_name}_index ON '{table_name}' ({column_name})")

    @lock
    @handle_exceptions
    def _execute_fetchone(self, query: str, values: Union[List, Tuple]) -> Tuple:
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        return cursor.fetchone()

    @lock
    @handle_exceptions
    def _execute_fetchall(self, query: str, values: Optional[Union[List, Tuple]] = None) -> List[Tuple]:
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