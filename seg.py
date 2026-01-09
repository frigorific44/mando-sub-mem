import pathlib
import pyhanlp


def segment(path: pathlib.Path) -> list[str]:
    word_set = dict()
    with open(path, encoding="utf-8") as subtitle_text:
        for line in subtitle_text:
            line = line.strip("\n")
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
