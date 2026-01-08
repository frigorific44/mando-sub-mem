import argparse
import pathlib

import deck


def main():
    parser = argparse.ArgumentParser(
        prog="mandosubmem", description="What the program does"
    )
    subparsers = parser.add_subparsers(
        required=True, dest="cmd", help="subcommand help"
    )

    parser_ext = subparsers.add_parser("ext", help="ext help")

    parser_dec = subparsers.add_parser("dec")
    parser_dec.add_argument("-d", "--dictionary", required=True)
    parser_dec.add_argument(
        "-c", "--char-set", choices=["traditional", "simplified"], required=True
    )
    parser_dec.add_argument("-i", "--input", required=True)
    parser_dec.add_argument("-n", "--name", required=True)

    args = parser.parse_args()
    # print(args)
    if args.cmd == "ext":
        print("ext")
    elif args.cmd == "dec":
        dec_command(parser_dec, args)


def dec_command(parser, args):
    dict_path = pathlib.Path(args.dictionary)
    input_path = pathlib.Path(args.input)
    if not dict_path.is_file():
        parser.print_usage()
        print("Dictionary is not a file path.")
    deck.deck(dict_path, args.char_set, input_path, args.name)


if __name__ == "__main__":
    main()
