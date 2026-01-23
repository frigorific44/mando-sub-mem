import pyhanlp
from htpy import div, h1, hr, rt, ruby

from mandosubmem.deckbuilder.base import BaseDeck


class ZH_Deck(BaseDeck):
    template = [
        h1(".hide-rcl-f")[ruby["{{term}}", rt(".hide-rcg-f")["{{pinyin}}"]]],
        hr,
        div(".hide-rcg-f")["{{gloss}}"],
    ]

    @property
    def fields(self):
        return super().fields + ["pinyin"]

    def segment(self, sub_text: str) -> list[str]:
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

    def lookup_fallback(self, term: str):
        # Calculate combinations of substrings contained in the dictionary.
        def defined_combinations(runes: str) -> list[list[str]]:
            if runes == "":
                return [[]]
            combinations = []
            for i in range(len(runes)):
                curr = runes[: i + 1]
                if curr in self.db:
                    remainder = defined_combinations(runes[i + 1 :])
                    for r_combo in remainder:
                        combinations.append([curr, *r_combo])
            return combinations

        # Longer substrings are favored.
        def combination_metric(substring_combination: list[str]) -> int:
            return sum([len(w) ** 2 for w in substring_combination])

        all_combinations = defined_combinations(term)
        best_combination = max(
            [combination_metric(w_combo) for w_combo in all_combinations]
        )
        best_combinations_flat = [
            s
            for combination in all_combinations
            if combination_metric(combination) == best_combination
            for s in combination
        ]
        return best_combinations_flat
