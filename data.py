import os
import hashlib
import compression.zstd as zstd


   
def init(args):
    root_folder=args.directory
    ding_folder=os.path.join(root_folder, ".ding")
    if(os.path.isdir(ding_folder)):
        print("Path already exists. Delete .ding to reinitialize.")
        return
    refs_folder=os.path.join(ding_folder, "refs")
    objects_folder=os.path.join(ding_folder, "objects")
    os.makedirs(refs_folder, exist_ok=True)
    os.makedirs(objects_folder, exist_ok=True)
    print("Initialized empty repository")


def find_repo(curr_dir):
    parent = os.path.dirname(curr_dir)
    if parent==curr_dir:
        return
    full_path = os.path.join(curr_dir, ".ding")
    if os.path.isdir(full_path):
        return full_path
    else:
        return find_repo(parent)



def hash_object(args):
    filename=args.file
    with open(filename,"rb") as file:
        content= file.read()

    hash_value=hashlib.sha1(content).hexdigest()
    compressed = zstd.compress(content, level=3)

    repo_path=find_repo(os.getcwd())
    if repo_path is None:
        print("could not find repo base folder. Make sure to run ding init first.")
        return
    objects_folder=os.path.join(repo_path, "objects")
    object_file=os.path.join(objects_folder, hash_value)
    with open(object_file,"wb") as file:
        file.write(compressed)
    print(hash_value)


def cat_file(args):
    oid=args.oid

    repo_path=find_repo(os.getcwd())
    if repo_path is None:
        print("could not find repo base folder. Make sure to run ding init first.")
        return
    objects_folder=os.path.join(repo_path, "objects")
    object_file=os.path.join(objects_folder, oid)

    if(os.path.isfile(object_file)):
        with open(object_file,"rb") as file:
                compressed= file.read()
    else:
        print("File does not exitst!")
        return

    content=zstd.decompress(compressed).decode("utf-8")
    print(content)
