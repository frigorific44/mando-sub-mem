import argparse
import pathlib

import mandosubmem.deck as deck
import mandosubmem.ext as ext


def cli():
    parser = argparse.ArgumentParser(
        prog="mandosubmem",
        description="Build Anki decks from subtitles for Chinese language-learning.",
    )
    subparsers = parser.add_subparsers(
        required=True, dest="cmd", help="one of the subcommands must be provided"
    )

    parser_ext = subparsers.add_parser(
        "ext", help="extract subtitles from a video file"
    )
    parser_ext.add_argument(
        "-i", "--input", required=True, help="video file to extract subtitle from"
    )
    parser_ext.add_argument(
        "-o",
        "--output",
        help="output file to write subtitles to if provided, otherwise they're written to stdout",
    )

    parser_dec = subparsers.add_parser(
        "dec", help="generate an Anki deck from subtitles."
    )
    parser_dec.add_argument(
        "-d", "--dictionary", required=True, help="a CC-CEDICT dictionary file"
    )
    parser_dec.add_argument(
        "-c",
        "--char-set",
        choices=["traditional", "simplified"],
        required=True,
        help="whether the subtitles and generated cards are targeting Traditional or Simplified Chinese",
    )
    parser_dec.add_argument(
        "-i",
        "--input",
        required=True,
        help="either an .srt file or a video file with a text subtitle stream",
    )
    parser_dec.add_argument("-n", "--name", required=True, help="the name of the deck")

    args = parser.parse_args()
    # print(args)
    if args.cmd == "ext":
        ext_command(parser_ext, args)
    elif args.cmd == "dec":
        dec_command(parser_dec, args)


def ext_command(parser, args):
    input_path = pathlib.Path(args.input)
    if not input_path.is_file():
        parser.print_usage()
        print("Input to extract from is not a file.")
        return
    stream_options = ext.get_subtitle_streams(input_path)
    subs = ext.ext(input_path, list_prompt(list(stream_options.values())))
    if args.output:
        output_path = pathlib.Path(args.output)
        output_path.write_text(subs, encoding="utf-8")
    else:
        print(subs)


def subtitles_prompt(input_path: pathlib.Path):
    stream_options = ext.get_subtitle_streams(input_path)
    for k, v in stream_options.items():
        print(f"{k}: {v}")
    chosen = ""
    while chosen not in stream_options:
        chosen = input("Choose a stream: ")
    return chosen


def list_prompt(prompt_list):
    for i in range(len(prompt_list)):
        print(f"{i}: {prompt_list[i]}")
    chosen = -1
    while chosen < 0 or chosen >= len(prompt_list):
        input_str = input(f"Choose (0 - {len(prompt_list) - 1}): ")
        try:
            chosen = int(input_str)
        except ValueError:
            pass
    return chosen


def dec_command(parser, args):
    dict_path = pathlib.Path(args.dictionary)
    input_path = pathlib.Path(args.input)
    if not dict_path.is_file():
        parser.print_usage()
        print("Dictionary is not a file path.")
        return
    if not input_path.is_file():
        parser.print_usage()
        print("Input is not a file.")
        return
    if args.name == "":
        parser.print_usage()
        print("Deck name cannot be an empty string.")
        return
    if input_path.suffix == ".srt":
        subs = input_path.read_text(encoding="utf-8")
    else:
        subs = ext.ext(input_path, int(subtitles_prompt(input_path)) - 2)
    deck.deck(dict_path, args.char_set, subs, args.name)


if __name__ == "__main__":
    cli()
