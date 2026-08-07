# Ding - Version Control System

A simple, content-addressable version control system built from scratch in Python.

## Features

Ding implements the core functionality of a local version control system:

* **Repository Management:** Initialize repositories and track changes.
* **Content Hashing:** Store file snapshots using SHA-1 hashing and zstd compression.
* **Staging Area:** Add files to an index before committing.
* **History Tracking:** Create commits that link to parents to form a history graph.
* **Branching & Checkout:** Create alternate timelines and restore your working directory to past states.



## Installation

Ensure you have Python installed. It is recommended to install this project inside a virtual environment.

1. Clone or download this repository.
2. Navigate to the root folder of the project in your terminal.
3. Create a virtual environment:
```bash
   python -m venv venv

```

4. Activate the virtual environment:
* **On Windows:**
```bash
venv\Scripts\activate

```


* **On macOS/Linux:**
```bash
source venv/bin/activate

```




5. Install the CLI tool using pip:
```bash
pip install -e .

```



You can now use the `ding` command from any directory on your computer, as long as this virtual environment remains active.

## Available Commands

### High-level Commands

* `ding init [directory]` - Initialize a new empty repository (creates the `.ding` hidden folder).
* `ding add <file>` - Hash a file and add it to the staging index.
* `ding commit -m "<message>"` - Snapshot the staging area and record a new commit.
* `ding log` - Traverse and print the commit history for the current branch.
* `ding branch <branch_name>` - Create a new branch pointing to the current commit.
* `ding checkout <branch_name>` - Switch branches and overwrite the working directory files to match that branch.

### Low-level Commands

* `ding hash-object <file>` - Hash a file, compress it, and store it in the object database.
* `ding cat-file <oid>` - Decompress and print the contents of a stored object.
* `ding write-tree` - Create a tree object from the current index.

## Example Workflow

```bash
# Initialize a new repository
ding init

# Create a file and add it to the staging area
echo "print('hello world')" > script.py
ding add script.py

# Commit the changes
ding commit -m "Initial commit"

# Check the history
ding log

# Create a new branch
ding branch feature-test
ding checkout feature-test

```

