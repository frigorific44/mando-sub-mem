import argparse
import pathlib

import deck
import ext


def main():
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
        "-i", "--input", required=True, help="the SRT subtitle file"
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
    stream_options = ext.get_subtitle_streams(input_path)
    for k, v in stream_options.items():
        print(f"{k}: {v}")
    chosen = ""
    while chosen not in stream_options:
        chosen = input("Choose a stream: ")
    out = ext.ext(input_path, int(chosen) - 2)
    if args.output:
        output_path = pathlib.Path(args.output)
        output_path.write_text(out, encoding="utf-8")
    else:
        print(out)


def dec_command(parser, args):
    dict_path = pathlib.Path(args.dictionary)
    input_path = pathlib.Path(args.input)
    if not dict_path.is_file():
        parser.print_usage()
        print("Dictionary is not a file path.")
        return
    if args.name == "":
        parser.print_usage()
        print("Deck name cannot be an empty string.")
        return
    deck.deck(dict_path, args.char_set, input_path, args.name)


if __name__ == "__main__":
    main()
