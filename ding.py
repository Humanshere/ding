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

add_parser=subparser.add_parser("add")
add_parser.add_argument("file")
add_parser.set_defaults(func=data.add)

cat_file_parser=subparser.add_parser("cat-file")
cat_file_parser.add_argument("oid")
cat_file_parser.set_defaults(func=data.cat_file)


write_tree_parser=subparser.add_parser("write-tree")
write_tree_parser.set_defaults(func=data.write_tree)


commit_parser=subparser.add_parser("commit")
commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
commit_parser.set_defaults(func=data.commit)

log_parser=subparser.add_parser("log")
log_parser.set_defaults(func=data.log)

branch_parser=subparser.add_parser("branch")
branch_parser.add_argument("branch_name")
branch_parser.set_defaults(func=data.branch)

checkout_parser=subparser.add_parser("checkout")
checkout_parser.add_argument("branch_name")
checkout_parser.set_defaults(func=data.checkout)

args=parser.parse_args()

if hasattr(args, "func"):
    args.func(args)
else:
    parser.print_help()
