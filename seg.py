import pyhanlp

numerals = set(
    [
        "零",
        "〇",
        "一",
        "二",
        "三",
        "四",
        "五",
        "六",
        "七",
        "八",
        "九",
        "十",
        "百",
        "千",
        "万",
        "亿",
    ]
)


def segment(path):
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
                        # print(term.word)
                        # print(term.nature)
                    # if str(term.nature) == "m":
                    #     print(term.word)
    # print(word_set)
    print(len(word_set))
    for word in word_set:
        if word[1] == "e":
            print(word)
