import argparse
import data

parser=argparse.ArgumentParser(description="A simple VCS written in python")
subparser=parser.add_subparsers()

init_parser=subparser.add_parser("init")
init_parser.add_argument("directory",default=".",nargs="?")
init_parser.set_defaults(func=data.init)


hash_object_parser=subparser.add_parser("hash-object")
hash_object_parser.add_argument("file")
hash_object_parser.set_defaults(func=data.hash_object)

cat_file_parser=subparser.add_parser("cat-file")
cat_file_parser.add_argument("oid")
cat_file_parser.set_defaults(func=data.cat_file)

args=parser.parse_args()

if hasattr(args, "func"):
    args.func(args)
else:
    parser.print_help()
