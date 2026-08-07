import argparse
import data

parser = argparse.ArgumentParser(
    prog="ding",
    description="A simple version control system written in Python"
)
subparser = parser.add_subparsers()

init_parser = subparser.add_parser("init", help="Initialize a new empty repository")
init_parser.add_argument("directory", default=".", nargs="?", help="Target directory (default: current)")
init_parser.set_defaults(func=data.init)

hash_object_parser = subparser.add_parser("hash-object", help="Hash a file and store it in objects")
hash_object_parser.add_argument("file", help="File to hash")
hash_object_parser.set_defaults(func=data.hash_object)

add_parser = subparser.add_parser("add", help="Add file to staging area")
add_parser.add_argument("file", help="File to stage")
add_parser.set_defaults(func=data.add)

cat_file_parser = subparser.add_parser("cat-file", help="Print object content from its ID")
cat_file_parser.add_argument("oid", help="Object ID")
cat_file_parser.set_defaults(func=data.cat_file)

write_tree_parser = subparser.add_parser("write-tree", help="Create tree object from staging area")
write_tree_parser.set_defaults(func=data.write_tree)

commit_parser = subparser.add_parser("commit", help="Commit staged changes")
commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
commit_parser.set_defaults(func=data.commit)

log_parser = subparser.add_parser("log", help="Show commit history")
log_parser.set_defaults(func=data.log)

branch_parser = subparser.add_parser("branch", help="Create a new branch")
branch_parser.add_argument("branch_name", help="Name of new branch")
branch_parser.set_defaults(func=data.branch)

checkout_parser = subparser.add_parser("checkout", help="Switch branches")
checkout_parser.add_argument("branch_name", help="Branch name to switch to")
checkout_parser.set_defaults(func=data.checkout)


def main():
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()