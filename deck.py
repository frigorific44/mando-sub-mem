import pathlib
import random
import re
from collections import namedtuple

import genanki

brackets_exp = re.compile(r"(?<=\[).+?(?=\])")
syllable_exp = re.compile(r"[a-z]+[1-5](?!\d)", re.IGNORECASE)
tone_exp = re.compile(r"(a|e|o(?=u)|[oiuü](?=$|n))", re.IGNORECASE)
tones = ["\u0304", "\u0301", "\u030c", "\u0300", "\u200b"]
mem_model = genanki.Model(
    model_id=1743404006,
    name="MandoSubMem",
    fields=[
        {"name": "Simplified"},
        {"name": "Traditional"},
        {"name": "Pinyin"},
        {"name": "Gloss"},
    ],
    templates=[
        {
            "name": "Recognition-Simplified",
            "qfmt": '<div class="hanzi">{{Simplified}}</div>',
            "afmt": '<ruby class="hanzi">{{Simplified}}<rt>{{Pinyin}}</rt></ruby><hr id=answer>{{Gloss}}',
        },
        {
            "name": "Recollection-Simplified",
            "qfmt": "<!-- Simplified -->{{Gloss}}",
            "afmt": '<ruby class="hanzi">{{Simplified}}<rt>{{Pinyin}}</rt></ruby><hr id=answer>{{Gloss}}',
        },
        {
            "name": "Recognition-Traditional",
            "qfmt": '<div class="hanzi">{{Traditional}}</div>',
            "afmt": '<ruby class="hanzi">{{Traditional}}<rt>{{Pinyin}}</rt></ruby><hr id=answer>{{Gloss}}',
        },
        {
            "name": "Recollection-Traditional",
            "qfmt": "<!-- Traditional -->{{Gloss}}",
            "afmt": '<ruby class="hanzi">{{Traditional}}<rt>{{Pinyin}}</rt></ruby><hr id=answer>{{Gloss}}',
        },
    ],
    css="""
.card {
    font-family: sans-serif;
    font-size: 24px;
    line-height: 2;
    text-align: center;
}

.hanzi {
    font-size: 36px;
}
""",
)

# TODO: Should configure the note to only call hash function on everything but the glossary.
# class MandoNote(genanki.Note):
#     @property
#     def guid(self):
#         return genanki.guid_for(self.fields[0], self.fields[1])


def pinyin_num_to_diacritic(syllable: str) -> str:
    if len(syllable) < 1 or not syllable[-1].isdigit():
        print(syllable)
        return syllable
    tone_num = int(syllable[-1]) - 1
    if tone_num < 0 or tone_num >= len(tones):
        print(syllable)
        return syllable
    tone = tones[tone_num]
    syllable = syllable[:-1]
    syllable.replace("u:", "ü")
    syllable = tone_exp.sub(r"\1" + tone, syllable, 1)
    return syllable


def deck(
    dict_path: pathlib.Path, char_set: str, input_path: pathlib.Path, deck_name: str
):
    ce_dict = dict()
    TermEntry = namedtuple(
        "TermEntry", ["simplified", "traditional", "pinyin", "gloss"]
    )
    with open(dict_path, encoding="utf-8") as dict_text:
        for line in dict_text:
            if not line.startswith("#"):
                break
        for line in dict_text:
            line = line.strip("\n")

            def pinyin_repl(match: re.Match) -> str:
                return pinyin_num_to_diacritic(match[0])

            def syllable_repl(match: re.Match) -> str:
                return syllable_exp.sub(pinyin_repl, match[0])

            # Give pinyin number-toned syllables diacritics instead.
            line = brackets_exp.sub(syllable_repl, line)

            sense_boundary = line.strip("/").split("/")
            senses = sense_boundary[1:]
            pinyin_boundary = sense_boundary[0].split("[")
            pinyin = pinyin_boundary[-1].rstrip("] ")
            term_boundary = pinyin_boundary[0].split()
            traditional = term_boundary[0]
            simplified = term_boundary[1]
            gloss = "<br>".join(senses)
            entry = TermEntry(simplified, traditional, pinyin, gloss)
            # TODO: Check if entry already exists. Otherwise it will be overwritten.
            if char_set == "traditional":
                ce_dict[traditional] = entry
            else:
                ce_dict[simplified] = entry

    to_add = set()
    for word in input_path.read_text(encoding="UTF-8").split("\n"):
        if word in ce_dict:
            to_add.add(word)
        else:
            # Calculate combinations of substrings contained in the dictionary.
            def defined_substr_combos(runes: str) -> list[list[str]]:
                if runes == "":
                    return [[]]
                combos = []
                for i in range(len(runes)):
                    curr = runes[: i + 1]
                    if curr in ce_dict:
                        remainder = defined_substr_combos(runes[i + 1 :])
                        for r_combo in remainder:
                            combos.append([curr, *r_combo])
                return combos

            # Longer substrings are favored.
            def combo_metric(combo: list[str]) -> int:
                return sum([len(w) ** 2 for w in combo])

            w_combos = defined_substr_combos(word)
            max_combo = max([combo_metric(w_combo) for w_combo in w_combos])
            w_combos = [
                w_combo for w_combo in w_combos if combo_metric(w_combo) == max_combo
            ]
            for combo in w_combos:
                for w in combo:
                    to_add.add(w)

    new_deck = genanki.Deck(deck_id=random.randrange(1 << 30, 1 << 31), name=deck_name)
    for word in to_add:
        entry = ce_dict[word]
        new_note = genanki.Note(model=mem_model, fields=[*entry])
        new_deck.add_note(new_note)

    genanki.Package(new_deck).write_to_file("output.apkg")
