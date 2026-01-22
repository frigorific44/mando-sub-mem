import json
import pathlib


class EntryStore:
    def __init__(self, entry, get_entries):
        self._Entry = entry
        self._datapath = pathlib.Path(__file__).parent.joinpath(entry.__name__)
        self._get_entries = get_entries
        self._db = None

    @property
    def db(self):
        if self._db:
            return self._db
        if not self._datapath.exists():
            self._db = self._get_entries(self._Entry)
            if not self._db:
                with self._datapath.open(mode="w") as f:
                    json.dump(self._db, f)
        else:
            with self._datapath.open(mode="r") as f:
                self._db = json.load(f)
        return self._db

    # def open(self):
    #     if not self._datapath.exists():
    #         with shelve.open(self._datapath, flag="n") as db:
    #             # db.update(self._get_entries(self._Entry))
    #             for key, entry in self._get_entries(self._Entry).items():
    #                 db[key] = self._Entry(entry)
    #     return shelve.open(self._datapath, flag="r")
