import pathlib
import random
import re
from collections import defaultdict, namedtuple

import genanki
from htpy import div, h1, h2, hr, p, rt, ruby, span
from markupsafe import Markup

# This is all to ensure the two models contain identical formatting.
# Two separate models are maintained because Traditional and Simplified characters
# are not one to one, and glosses are combined on characters, so cards will be
# different depending on which character set is the focus.
model_css = """
.card {
    font-family: sans-serif;
    font-size: 24px;
    line-height: 1.5;
    text-align: center;
}

hr {
    background-color: #000000;
    height: 2px;
    margin: 0;
}

h1 {
    font-size: 36px;
}

.gloss h2 {
    font-size: 24px;
    text-decoration-line: underline;
    text-decoration-thickness: 2px;
    text-underline-offset: 0.5em;
    margin: 0;
}

.gloss p {
    margin: 0;
    margin-top: 0.5em;
}

.front.recognition rt {
    opacity: 0;
}

.front.recognition .gloss {
    opacity: 0;
}

.front.recollection h1 {
    opacity: 0;
}
"""
model_fields = [
    {"name": "Simplified"},
    {"name": "Traditional"},
    {"name": "Pinyin"},
    {"name": "Gloss"},
]


def tmpl(char_set, side, card):
    tmpl = div(f".{side} .{card}")[
        h1[ruby[f"{{{{{char_set}}}}}", rt["{{Pinyin}}"]]],
        hr,
        div(".gloss")["{{Gloss}}"],
    ]
    return str(tmpl)


traditional_model = genanki.Model(
    model_id=1743404006,
    name="MandoSubMem-Traditional",
    fields=model_fields,
    templates=[
        {
            "name": "Recognition",
            "qfmt": tmpl("Traditional", "front", "recognition"),
            "afmt": tmpl("Traditional", "back", "recognition"),
        },
        {
            "name": "Recollection",
            "qfmt": tmpl("Traditional", "front", "recollection"),
            "afmt": tmpl("Traditional", "back", "recollection"),
        },
    ],
    css=model_css,
)
simplified_model = genanki.Model(
    model_id=1790468694,
    name="MandoSubMem-Simplified",
    fields=model_fields,
    templates=[
        {
            "name": "Recognition",
            "qfmt": tmpl("Simplified", "front", "recognition"),
            "afmt": tmpl("Simplified", "back", "recollection"),
        },
        {
            "name": "Recollection",
            "qfmt": tmpl("Simplified", "front", "recollection"),
            "afmt": tmpl("Simplified", "back", "recollection"),
        },
    ],
    css=model_css,
)


class MandoNote(genanki.Note):
    @property
    def guid(self):
        if self.fields is not None:
            return genanki.guid_for(*self.fields[:3])
        return super().guid()


TermEntry = namedtuple(
    "TermEntry",
    ["simplified", "traditional", "pinyin", "gloss"],
    defaults=["", "", "", ""],
)


def deck(
    dict_path: pathlib.Path, char_set: str, input_path: pathlib.Path, deck_name: str
):
    ce_dict = defaultdict(list)
    with open(dict_path, encoding="utf-8") as dict_text:
        for line in dict_text:
            if not line.startswith("#"):
                break
        for line in dict_text:
            line = line.strip("\n")
            line = cedict_pinyin_num_to_diacritic(line)
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
                ce_key = traditional
            else:
                ce_key = simplified
            # if ce_key in ce_dict:
            #     print(ce_key)
            ce_dict[ce_key].append(entry)

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
    mem_model = traditional_model if char_set == "traditional" else simplified_model
    for word in to_add:
        note_fields = reconcile_entries(ce_dict[word])
        new_note = MandoNote(model=mem_model, fields=[*note_fields])
        new_deck.add_note(new_note)

    genanki.Package(new_deck).write_to_file("output.apkg")


def cedict_pinyin_num_to_diacritic(s: str) -> str:
    brackets_exp = re.compile(r"(?<=\[).+?(?=\])")
    syllable_exp = re.compile(r"[a-z]+[1-5](?!\d)", re.IGNORECASE)
    tone_exp = re.compile(r"(a|e|o(?=u)|[oiuü](?=$|n))", re.IGNORECASE)
    tones = ["\u0304", "\u0301", "\u030c", "\u0300", "\u200b"]

    def pinyin_repl(match: re.Match) -> str:
        syllable = match[0]
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

    def syllable_repl(match: re.Match) -> str:
        return syllable_exp.sub(pinyin_repl, match[0])

    # Give pinyin number-toned syllables diacritics instead.
    return brackets_exp.sub(syllable_repl, s)


def reconcile_entries(entries: list[TermEntry]) -> tuple:
    if len(entries) == 1:
        return entries[0]
    # print(entries[0].simplified)

    reconciled_entry = ["", "", "", ""]
    # Set fields that are the same across all dictionary entries.
    field_sets = [set() for i in range(len(TermEntry()._fields))]
    for entry in entries:
        for i, field in enumerate(entry):
            field_sets[i].add(field.lower())
    for i in range(len(field_sets)):
        if len(field_sets[i]) == 1:
            reconciled_entry[i] = field_sets[i].pop()
    # Sort by pinyin, with proper nouns last, and add:
    for entry in sorted(entries, key=lambda t_entry: t_entry.pinyin.swapcase()):
        part = str(
            div[
                h2[
                    (
                        span[field]
                        for i, field in enumerate(entry)
                        if reconciled_entry[i] == ""
                        and i != TermEntry()._fields.index("gloss")
                    )
                ],
                p[Markup(entry.gloss)],
            ]
        )
        reconciled_entry[TermEntry()._fields.index("gloss")] += part

    return TermEntry(*reconciled_entry)
