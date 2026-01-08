import pathlib
import pyhanlp


def segment(path: pathlib.Path) -> str:
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
    # for word in word_set:
    #     if word[1] == "e":
    #         print(word)
    return "\n".join(word_set)
