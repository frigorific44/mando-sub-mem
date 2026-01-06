import random
import re
from collections import namedtuple

import genanki

pinyin_exp = re.compile(
    r"(?:[bpmfdtnlgkhjqxrzcsyw]|[zcs]h)[aeioung:]+\d", re.IGNORECASE
)
tone_placement_exp = re.compile(r"(a|e|o(?=u)|[oiuü](?=$|n))", re.IGNORECASE)
tones = ["\u0304", "\u0301", "\u030c", "\u0300"]
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
            "qfmt": "{{Gloss}}",
            "afmt": '<ruby class="hanzi">{{Simplified}}<rt>{{Pinyin}}</rt></ruby><hr id=answer>{{Gloss}}',
        },
        {
            "name": "Recognition-Traditional",
            "qfmt": '<div class="hanzi">{{Traditional}}</div>',
            "afmt": '<ruby class="hanzi">{{Traditional}}<rt>{{Pinyin}}</rt></ruby><hr id=answer>{{Gloss}}',
        },
        {
            "name": "Recollection-Traditional",
            "qfmt": "{{Gloss}}",
            "afmt": '<ruby class="hanzi">{{Traditional}}<rt>{{Pinyin}}</rt></ruby><hr id=answer>{{Gloss}}',
        },
    ],
)


# class MandoNote(genanki.Note):
#     @property
#     def guid(self):
#         return genanki.guid_for(self.fields[0], self.fields[1])


def pinyin_num_to_diacritic(syllable: str) -> str:
    if len(syllable) < 1 or not syllable[-1].isdigit():
        return syllable
    tone_num = int(syllable[-1])
    if tone_num < 0 or tone_num >= len(tones):
        return syllable
    tone = tones[tone_num]
    syllable = syllable[:-1]
    syllable.replace("u:", "ü")
    syllable = tone_placement_exp.sub(r"\1" + tone, syllable, 1)
    return syllable


def deck(dict_path, char_set, input_path, deck_name):
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

            def pinyin_repl(match):
                return pinyin_num_to_diacritic(match[0])

            line = pinyin_exp.sub(pinyin_repl, line)
            sense_boundary = line.strip("/").split("/")
            senses = sense_boundary[1:]
            pinyin_boundary = sense_boundary[0].split("[")
            pinyin = pinyin_boundary[-1].rstrip("] ")
            term_boundary = pinyin_boundary[0].split()
            traditional = term_boundary[0]
            simplified = term_boundary[1]
            gloss = "<br>".join(senses)
            entry = TermEntry(simplified, traditional, pinyin, gloss)
            # TODO: Check if entry already exists.
            if char_set == "traditional":
                ce_dict[traditional] = entry
            else:
                ce_dict[simplified] = entry

    to_add = set()
    for word in input_path.read_text(encoding="UTF-8").split("\n"):
        if word in ce_dict:
            to_add.add(word)
        else:
            # Calculate substring combinations
            def word_combos(runes):
                if runes == "":
                    return [[]]
                combos = []
                for i in range(len(runes)):
                    curr = runes[: i + 1]
                    if curr in ce_dict:
                        remainder = word_combos(runes[i + 1 :])
                        for r_combo in remainder:
                            combos.append([curr, *r_combo])
                return combos

            w_combos = word_combos(word)

            def combo_metric(combo):
                return sum([len(w) ** 2 for w in combo])

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
    # for k, v in ce_dict.items():
    #     print(k)
    #     print(v.gloss)
