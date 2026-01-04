from collections import namedtuple


def deck(dict_path, char_set, input_path, output_path):
    ce_dict = dict()
    TermEntry = namedtuple("TermEntry", ["pinyin", "gloss"])
    with open(dict_path, encoding="utf-8") as dict_text:
        for line in dict_text:
            if not line.startswith("#"):
                break
        for line in dict_text:
            line = line.strip("\n")
            sense_boundary = line.strip("/").split("/")
            senses = sense_boundary[1:]
            pinyin_boundary = sense_boundary[0].split("[")
            pinyin = pinyin_boundary[-1].rstrip("] ")
            term_boundary = pinyin_boundary[0].split()
            traditional = term_boundary[0]
            simplified = term_boundary[1]
            gloss = "\n".join(senses)
            entry = TermEntry(pinyin, gloss)
            if char_set == "traditional":
                ce_dict[traditional] = entry
            else:
                ce_dict[simplified] = entry
            print(line)
            print(gloss)
    # for k, v in ce_dict.items():
    #     print(k)
    #     print(v.gloss)
