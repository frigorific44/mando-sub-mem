import collections
import random

import genanki
from htpy import div, h1, hr

from mandosubmem.deckbuilder.entrystore import EntryStore
from mandosubmem.deckbuilder.models.base import LangModel


class LangNote(genanki.Note):
    @property
    def guid(self):
        if self.fields is not None:
            return genanki.guid_for(self.fields[0])
        return super().guid()


class BaseDeck:
    fields = ["Term", "Gloss"]
    template = [
        h1(".hide-rcl-f")["{{Term}}"],
        hr,
        div(".hide-rcg-f")["{{Gloss}}"],
    ]

    def __init__(self, model_id, name, db_initialization):
        """
        Args:
        model_id: An integer which should be generated once for the card type and hardcoded.
        name: A unique name.
        """
        self.model_id = model_id
        self.name = name
        self.db_initialization = db_initialization
        self._entrystore = None

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

    @property
    def db(self):
        if not self._entrystore:
            self._entrystore = EntryStore(self.Entry, self.db_initialization)
        return self._entrystore.db

    def build(self, sub_text: str):
        segments = self.__segment(sub_text)
        entries = self.__lookup(segments)
        deck = self.__gather(entries)
        self.__write(deck)

    def __segment(self, sub_text: str) -> list[str]:
        word_set = dict()
        for line in sub_text.split("\n"):
            if line != "" and not line[0].isdigit():
                for term in line.split():
                    if term not in word_set:
                        word_set[term] = True
        return list(word_set.keys())

    def __lookup(self, segments: list[str]):
        to_add = dict()
        entries = []
        for term in segments:
            if term not in self.db:
                for sub_term in self.__lookup_fallback(term, self.db):
                    if sub_term not in to_add:
                        to_add[term] = True
            elif term not in to_add:
                to_add[term] = True
        for term in to_add:
            entries.append(self.db[term])
        return to_add

    def __lookup_fallback(self, term: str, db):
        """
        Return potentionally less-accurate terms found within the database
        in place of a full lookup failure.
        """
        return []

    def __gather(self, entries):
        new_deck = genanki.Deck(
            deck_id=random.randrange(1 << 30, 1 << 31), name=f"SubMem::{self.name}"
        )
        print(f"Notes: {len(entries)}")
        for term in entries:
            new_note = LangNote(model=self.model, fields=[*self.fields])
            new_deck.add_note(new_note)
        return new_deck

    def __write(self, deck):
        genanki.Package(deck).write_to_file("output.apkg")
