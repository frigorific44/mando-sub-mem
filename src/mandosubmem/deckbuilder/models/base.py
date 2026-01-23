import genanki
from htpy import div

lang_css = """
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

.recognition.front .hide-rcg-f {
    opacity: 0;
}

.recognition.back .hide-rcg-b {
    opacity: 0;
}

.recollection.front .hide-rcl-f {
    opacity: 0;
}

.recollection.back .hide-rcl-b {
    opacity: 0;
}
"""


class LangModel(genanki.Model):
    """
    A generic model for language-learned flashcards.
    Subclasses can be created to prevent code duplication, but one-offs should make use
    of this base class if possible.
    """

    def __init__(self, model_id=None, name=None, fields=[], template="", css=""):
        """
        Initializes a LangModel instance.

        Args:
        model_id: An integer which should be generated once and hardcoded.
        name: A unique name.
        fields: A list of fields provided by BaseDeck or a subclass.
        template: The full card template to be modified for front, back, etc. with CSS.
            Should be an htpy object or a string without HTML tags.
        css: Additional CSS.
        """
        super().__init__(
            model_id=model_id,
            name=name,
            fields=[{"name": field} for field in fields],
            templates=[
                {
                    "name": "Recognition",
                    "qfmt": str(div(".recognition .front")[template]),
                    "afmt": str(div(".recognition .back")[template]),
                },
                {
                    "name": "Recollection",
                    "qfmt": str(div(".recollection .front")[template]),
                    "afmt": str(div(".recollection .back")[template]),
                },
            ],
            css=lang_css + "\n" + css,
        )
