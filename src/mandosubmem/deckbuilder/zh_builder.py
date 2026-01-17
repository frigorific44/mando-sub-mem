import pyhanlp
from htpy import div, h1, hr, rt, ruby

from mandosubmem.deckbuilder.base import BaseDeck


class ZH_Deck(BaseDeck):
    template = [
        h1(".hide-rcl-f")[ruby["{{Term}}", rt(".hide-rcg-f")["{{Pinyin}}"]]],
        hr,
        div(".hide-rcg-f")["{{Gloss}}"],
    ]

    @property
    def fields(self):
        return super().fields + ["Pinyin"]

    def __segment(self, sub_text: str) -> list[str]:
        word_set = dict()
        for line in sub_text.split("\n"):
            if line != "" and not line[0].isdigit():
                for term in pyhanlp.HanLP.segment(line):
                    if (
                        str(term.nature) not in set(["w", "nx"])
                        and not str(term.word).isdigit()
                    ):
                        if str(term.word) not in word_set:
                            word_set[str(term.word)] = True
        print(f"Segments: {len(word_set)}")
        return list(word_set)
