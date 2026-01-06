import deck
import seg
import pathlib
import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="mandosubmem", description="What the program does"
    )
    subparsers = parser.add_subparsers(
        required=True, dest="cmd", help="subcommand help"
    )

    parser_ext = subparsers.add_parser("ext", help="ext help")

    parser_seg = subparsers.add_parser("seg", help="seg help")
    parser_seg.add_argument("-i", "--input", required=True)
    parser_seg.add_argument("-o", "--output", required=True)

    parser_dec = subparsers.add_parser("dec")
    parser_dec.add_argument("-d", "--dictionary", required=True)
    parser_dec.add_argument(
        "-c", "--char-set", choices=["traditional", "simplified"], required=True
    )
    parser_dec.add_argument("-i", "--input", required=True)
    parser_dec.add_argument("-n", "--name", required=True)

    args = parser.parse_args()
    # print(args)
    if args.cmd == "seg":
        seg_command(parser_seg, args)
    elif args.cmd == "ext":
        print("ext")
    elif args.cmd == "dec":
        dec_command(parser_dec, args)


def seg_command(parser, args):
    input_path = pathlib.Path(args.input)
    if not input_path.is_file():
        parser.print_usage()
        print("Input is not a file path.")
    elif input_path.suffix != ".srt":
        print("Input is not a SubRip Text (.srt) file.")

    s = seg.segment(input_path)
    if args.output == "-":
        print(s)
    else:
        output_path = pathlib.Path(args.output)
        if output_path.is_file() and output_path.exists():
            while True:
                y_or_n = input("Would you like to overwrite? (y/n)")
                if y_or_n.startswith("y"):
                    break
                elif y_or_n.startswith("n"):
                    return
        output_path.write_text(s)


def dec_command(parser, args):
    dict_path = pathlib.Path(args.dictionary)
    input_path = pathlib.Path(args.input)
    if not dict_path.is_file():
        parser.print_usage()
        print("Dictionary is not a file path.")
    deck.deck(dict_path, args.char_set, input_path, args.name)


if __name__ == "__main__":
    main()
