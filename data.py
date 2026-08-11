import json
import os
import hashlib
import compression.zstd as zstd
import contextlib
import time


@contextlib.contextmanager
def acquire_lock(file_path):
    lock_path=file_path+".lock"
    while True:
        try:
            with open(lock_path,'x') as f:
                f.write(str(os.getpid()))
            break
        except FileExistsError:
            try:
                with open(lock_path, 'r') as f:
                    old_pid = int(f.read().strip())
                os.kill(old_pid, 0) # Sends a "null signal" to check if alive (Unix)
                print(f"Waiting for lock on {file_path}...")
                time.sleep(0.1)
            except (ProcessLookupError, FileNotFoundError, ValueError):
                if os.path.exists(lock_path):
                    os.remove(lock_path)
        continue 
    try:
        yield
    finally:
        if(os.path.exists(lock_path)):
            os.remove(lock_path)
        

def atomic_write(file_path,content,is_binary=False,is_json=False):
    tmp_path= file_path+f".tmp.{os.getpid()}"
    if is_binary:
        mode="wb"
    else:
        mode="w"

    with open(tmp_path,mode) as f:
        if is_json:
            json.dump(content,f,indent=4)
        else:
            f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path,file_path)


   
def init(args):
    root_folder=args.directory
    ding_folder=os.path.join(root_folder, ".ding")
    if(os.path.isdir(ding_folder)):
        print("Path already exists. Delete .ding to reinitialize.")
        return
    refs_folder=os.path.join(ding_folder, "refs")
    objects_folder=os.path.join(ding_folder, "objects")
    heads_folder=os.path.join(refs_folder,"heads")
    os.makedirs(refs_folder, exist_ok=True)
    os.makedirs(objects_folder, exist_ok=True)
    os.makedirs(heads_folder, exist_ok=True)
    head_file=os.path.join(ding_folder,"HEAD")
    with open(head_file,'w') as f:
        f.write("ref: refs/heads/main")
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


def store_content(content):
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
    if not os.path.exists(object_file):
        atomic_write(object_file,compressed,True)
    return hash_value

def store_file(filename):
    repo_path=find_repo(os.getcwd())
    if repo_path is None:
        print("could not find repo base folder. Make sure to run ding init first.")
        return None
    tmp_path = os.path.join(repo_path, "objects", f"tmp_obj_{os.getpid()}")
    hasher = hashlib.sha1()

    with open(filename,"rb") as file_in,zstd.open(tmp_path,"wb") as file_out:
        while True:
            chunk = file_in.read(4096 * 1024)
            if chunk == b'':
                break
            hasher.update(chunk)
            file_out.write(chunk)



    hash_value = hasher.hexdigest()
    objects_folder=os.path.join(repo_path, "objects")
    objects_subfolder=os.path.join(objects_folder, hash_value[:2])
    os.makedirs(objects_subfolder,exist_ok=True)
    object_file=os.path.join(objects_subfolder,hash_value[2:])
    if os.path.exists(object_file):
        os.remove(tmp_path)
    else:
        os.replace(tmp_path, object_file)
    return hash_value



def hash_object(args):
    filename=args.file
    hash_value=store_file(filename)
    if hash_value:
        print(hash_value)


def decompress(oid):
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

    content=zstd.decompress(compressed)
    return content

def cat_file(args):
    oid=args.oid
    print(decompress(oid).decode("utf-8"))
    


def add(args):
    filename=args.file
    absolute_path=os.path.abspath(filename)
    repo_path=find_repo(os.getcwd())
    if repo_path is None:
        print("could not find repo base folder. Make sure to run ding init first.")
        return
    repo_root = os.path.dirname(repo_path)
    relative_path=os.path.relpath(absolute_path, repo_root)
    index_file=os.path.join(repo_path,"index")
    if not os.path.exists(absolute_path):
        with acquire_lock(index_file):
            index_data={}
            if os.path.isfile(index_file):
                with open(index_file,'r')as json_file:
                    index_data=json.load(json_file)

            index_data.pop(relative_path,None)

            atomic_write(index_file,index_data,False,True)
            return
    hash_value=store_file(filename)
    with acquire_lock(index_file):
        index_data={}
        if os.path.isfile(index_file):
            with open(index_file,'r')as json_file:
                index_data=json.load(json_file)

        index_data[relative_path]=hash_value

        atomic_write(index_file,index_data,False,True)

        
def write_tree(args):
    repo_path=find_repo(os.getcwd())
    if repo_path is None:
        print("could not find repo base folder. Make sure to run ding init first.")
        return
    index_file=os.path.join(repo_path,"index")
    if not os.path.isfile(index_file):
        print("Nothing to commit (index is empty).")
        return

    hash_value=store_file(index_file)
    print(hash_value)
    return hash_value


def commit(args):
    repo_path=find_repo(os.getcwd())
    if repo_path is None:
            print("could not find repo base folder. Make sure to run ding init first.")
            return
    refs_folder=os.path.join(repo_path, "refs")
    heads_folder=os.path.join(refs_folder,"heads")
    pointer_file=os.path.join(repo_path,"HEAD")
    with open(pointer_file,'r') as f:
        branch=f.read()

    relative_path = branch.replace("ref: ", "", 1)
    parent_path = os.path.join(repo_path, *relative_path.split("/"))

    parent_hash=None
    if os.path.isfile(parent_path):
        with open(parent_path,'r') as f:
            parent_hash=f.read()
    hash_value=write_tree(args)
    if not hash_value:
        return
    commit_content=f"tree {hash_value}\n"
    if parent_hash:
        commit_content+=f"parent {parent_hash}\n"
    commit_content+=f"author Not implemented\n\n {args.message}"
    commit_hash=store_content(commit_content.encode("utf-8"))

    with acquire_lock(parent_path):
        atomic_write(parent_path,commit_hash)
    print(commit_hash)


def log(args):
    repo_path=find_repo(os.getcwd())
    if repo_path is None:
            print("could not find repo base folder. Make sure to run ding init first.")
            return
    pointer_file=os.path.join(repo_path,"HEAD")
    with open(pointer_file,'r') as f:
        branch=f.read()

    relative_path = branch.replace("ref: ", "", 1)
    parent_path = os.path.join(repo_path, *relative_path.split("/"))

    parent_hash=None
    if os.path.isfile(parent_path):
        with open(parent_path,'r') as f:
            parent_hash=f.read()
    else:
        print("No commits yet")

    objects_folder=os.path.join(repo_path,"objects")
    while parent_hash:
        content=decompress(parent_hash).decode("utf-8")
        print(parent_hash)
        print(content)
        headers, message = content.split("\n\n", 1) 
        words = headers.split()
        keyword="parent"
        if keyword in words:
            idx = words.index(keyword)
            parent_hash = words[idx + 1] if idx + 1 < len(words) else None
        else:
            parent_hash = None
   

def branch(args):
    repo_path=find_repo(os.getcwd())
    if repo_path is None:
            print("could not find repo base folder. Make sure to run ding init first.")
            return
    pointer_file=os.path.join(repo_path,"HEAD")
    with open(pointer_file,'r') as f:
        branch=f.read()

    relative_path = branch.replace("ref: ", "", 1)
    branch_path = os.path.join(repo_path, *relative_path.split("/"))

    commit_hash=None
    if os.path.isfile(branch_path):
        with open(branch_path,'r') as f:
            commit_hash=f.read()

    if not commit_hash:
        print("Fatal: Main can't be empty, make a commit first")
        return


    branch_file=os.path.join(repo_path,"refs","heads",args.branch_name)
    with acquire_lock(branch_file):
        atomic_write(branch_file, commit_hash)

def checkout(args):
    repo_path=find_repo(os.getcwd())
    if repo_path is None:
        print("could not find repo base folder. Make sure to run ding init first.")
        return
    branch_file=os.path.join(repo_path,"refs","heads",args.branch_name)
    if not os.path.isfile(branch_file):
        print("branch with name "+args.branch_name+" does not exist")
        return 
    with open(branch_file,'r') as f:
        commit_hash=f.read()   

    content=decompress(commit_hash).decode("utf-8")
    headers, message = content.split("\n\n", 1) 
    words = headers.split()
    keyword="tree"
    if keyword in words:
        idx = words.index(keyword)
        tree_hash = words[idx + 1] if idx + 1 < len(words) else None
    else:
        tree_hash = None

    new_tree=json.loads(decompress(tree_hash).decode("utf-8"))
    index_file=os.path.join(repo_path,"index")
    curr_tree = {}
    if os.path.exists(index_file):
        with open(index_file) as f:
            curr_tree=json.load(f)


    files_to_add={}
    for filepath, blob_hash in new_tree.items():
        if filepath not in curr_tree or blob_hash!=curr_tree[filepath]:
            files_to_add[filepath]=blob_hash

    repo_root = os.path.dirname(repo_path)


    for filepath in curr_tree:
        absolute_path = os.path.join(repo_root, filepath)
        if filepath not in new_tree:
            os.remove(absolute_path)
            try:
                os.removedirs(os.path.dirname(absolute_path))
            except OSError:
                pass


    for filepath, blob_hash in files_to_add.items():
        absolute_path = os.path.join(repo_root, filepath)
        new_content=decompress(blob_hash)
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
        with open(absolute_path, 'wb') as new_file:
            new_file.write(new_content)    

    atomic_write(index_file,new_tree,is_json=True)

    pointer_file=os.path.join(repo_path,"HEAD")
    with acquire_lock(pointer_file):
        atomic_write(pointer_file, "ref: refs/heads/"+args.branch_name)

    print(f"Switched to branch '{args.branch_name}'")