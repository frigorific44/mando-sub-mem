import pathlib
import pyhanlp


def segment(path: pathlib.Path) -> str:
    word_set = set()
    with open(path, encoding="utf-8") as subtitle_text:
        for line in subtitle_text:
            line = line.strip("\n")
            if line != "" and not line[0].isdigit():
                for term in pyhanlp.HanLP.segment(line):
                    if (
                        str(term.nature) not in set(["w", "nx"])
                        and not str(term.word).isdigit()
                    ):
                        word_set.add((str(term.word), str(term.nature)))
    print(len(word_set))
    # for word in word_set:
    #     if word[1] == "e":
    #         print(word)
    return "\n".join([word[0] for word in word_set])
