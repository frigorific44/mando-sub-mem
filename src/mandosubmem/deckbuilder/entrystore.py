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
            if self._db:
                with self._datapath.open(mode="w") as f:
                    json.dump(self._db, f, ensure_ascii=False, sort_keys=True, indent=4)
        else:
            with self._datapath.open(mode="r") as f:
                self._db = {k: self._Entry(*v) for k, v in json.load(f).items()}
        return self._db
