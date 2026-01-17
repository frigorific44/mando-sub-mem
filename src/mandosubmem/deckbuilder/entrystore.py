from typing import NamedTuple
from collections.abc import Callable
import pathlib
import shelve


class EntryStore:
    def __init__(self, entry: NamedTuple, get_entries: Callable[[], dict]):
        self._Entry = entry
        self._datapath = pathlib.Path(type(entry).__name__)
        self._get_entries = get_entries

    def open(self):
        if not self._datapath.exists():
            with shelve.open(self._datapath, flag="n") as db:
                for key, entry in self._get_entries().items():
                    db[key] = self._Entry(entry)
        return shelve.open(self._datapath, flag="r")
