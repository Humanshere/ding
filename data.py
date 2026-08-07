import json
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


def store_object(filename):
    with open(filename,"rb") as file:
        content= file.read()

    hash_value=hashlib.sha1(content).hexdigest()
    compressed = zstd.compress(content, level=3)

    repo_path=find_repo(os.getcwd())
    if repo_path is None:
        print("could not find repo base folder. Make sure to run ding init first.")
        return None
    objects_folder=os.path.join(repo_path, "objects")
    objects_subfolder=os.path.join(objects_folder, hash_value[:2])
    os.makedirs(objects_subfolder,exist_ok=True)
    object_file=os.path.join(objects_subfolder,hash_value[2:])
    with open(object_file,"wb") as file:
        file.write(compressed)
    return hash_value



def hash_object(args):
    filename=args.file
    hash_value=store_object(filename)
    if hash_value:
        print(hash_value)


def cat_file(args):
    oid=args.oid

    repo_path=find_repo(os.getcwd())
    if repo_path is None:
        print("could not find repo base folder. Make sure to run ding init first.")
        return
    objects_folder=os.path.join(repo_path, "objects")
    objects_subfolder=os.path.join(objects_folder, oid[:2])
    object_file=os.path.join(objects_subfolder,oid[2:])
    
    if(os.path.isfile(object_file)):
        with open(object_file,"rb") as file:
                compressed= file.read()
    else:
        print("File does not exitst!")
        return

    content=zstd.decompress(compressed).decode("utf-8")
    print(content)


def add(args):
    filename=args.file
    hash_value=store_object(filename)
    repo_path=find_repo(os.getcwd())
    if repo_path is None:
        print("could not find repo base folder. Make sure to run ding init first.")
        return
    index_file=os.path.join(repo_path,"index")
    index_data={}
    if os.path.isfile(index_file):
        with open(index_file,'r')as json_file:
            index_data=json.load(json_file)

    index_data[filename]=hash_value

    with open(index_file,'w')as json_file:
        json.dump(index_data,json_file,indent=4)