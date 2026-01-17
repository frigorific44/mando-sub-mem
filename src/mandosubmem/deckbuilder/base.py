import collections

from htpy import div, h1, hr

from mandosubmem.deckbuilder.models.base import LangModel


class BaseDeck:
    fields = ["Term", "Gloss"]
    template = [
        h1(".hide-rcl-f")["{{Term}}"],
        hr,
        div(".hide-rcg-f")["{{Gloss}}"],
    ]

    def __init__(self, model_id, name, db):
        """
        Args:
        model_id: An integer which should be generated once for the card type and hardcoded.
        name: A unique name.
        """
        self.model_id = model_id
        self.name = name
        self.db = db

    @property
    def model(self):
        model = LangModel(
            model_id=self.model_id,
            name=self.name,
            fields=self.fields,
            template=self.template,
        )
        return model

    @property
    def Entry(self):
        return collections.namedtuple(self.name, self.fields)

    # basestore = EntryStore(Entry, zh_get_entries)

    def build(self, sub_text: str):
        segments = self.__segment(sub_text)
        entries = self.__lookup(segments)

    def __segment(self, sub_text: str) -> list[str]:
        word_set = dict()
        for line in sub_text.split("\n"):
            if line != "" and not line[0].isdigit():
                for term in line.split():
                    if term not in word_set:
                        word_set[term] = True
        return list(word_set.keys())

    def __lookup(self, segments: list[str]):
        entries = []
        leftover = []
        with self.db.open() as db:
            for term in segments:
                if term in db:
                    entries.append(db[term])
                else:
                    leftover.append(term)
        # TODO: Handle out-of-dictionary segments.
        return entries
