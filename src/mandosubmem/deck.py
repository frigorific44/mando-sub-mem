import pathlib
import random
import re
from collections import defaultdict

import genanki
from htpy import div, h2, p, span
from markupsafe import Markup

from .models.chinese import MandoNote, TermEntry, simplified_model, traditional_model
from mandosubmem.seg import segment


def deck(dict_path: pathlib.Path, char_set: str, sub_text: str, deck_name: str):
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
            if char_set == "traditional":
                ce_key = traditional
            else:
                ce_key = simplified
            # if ce_key in ce_dict:
            #     print(ce_key)
            ce_dict[ce_key].append(entry)

    to_add = dict()
    for word in segment(sub_text):
        if word in ce_dict:
            if word not in to_add:
                to_add[word] = True
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
                    if word not in to_add:
                        to_add[w] = True
                    pass

    new_deck = genanki.Deck(
        deck_id=random.randrange(1 << 30, 1 << 31), name=f"MandoSubMem::{deck_name}"
    )
    mem_model = traditional_model if char_set == "traditional" else simplified_model
    print(f"Notes: {len(to_add)}")
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
