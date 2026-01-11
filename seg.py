import pyhanlp


def segment(sub_text: str) -> list[str]:
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
