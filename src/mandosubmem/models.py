from collections import namedtuple

import genanki
from htpy import div, h1, hr, rt, ruby

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
            return genanki.guid_for(self.fields[0])
        return super().guid()


TermEntry = namedtuple(
    "TermEntry",
    ["simplified", "traditional", "pinyin", "gloss"],
    defaults=["", "", "", ""],
)
