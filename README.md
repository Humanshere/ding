# Ding - Version Control System

A robust, content-addressable version control system built from scratch in Python. 

While simple on the surface, Ding's underlying engine implements advanced version control mechanics including ACID-compliant database operations, memory-efficient streaming for large binaries, and algorithmic tree-diffing.

## Features

* **Repository Management:** Initialize repositories and track changes across branches.
* **Content Hashing:** Store file snapshots using SHA-1 hashing and `zstd` compression.
* **Large File Streaming:** Memory-safe chunk streaming handles massive binary files (videos, images) without Out-Of-Memory (OOM) crashes.
* **ACID Compliance:** Atomic file swaps and crash-safe process locks prevent repository corruption during concurrent operations.
* **Smart Checkout:** Tree-diffing algorithms compare branches and surgically update only the exact files that changed, minimizing disk I/O.
* **Staging Area:** Add specific files or recursively add entire directories, automatically detecting new, modified, and deleted files.
* **History Tracking:** Create commits that link to parents to form a cryptographic history graph (DAG).

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

You can now use the `ding` command from any directory on your computer, as long as this virtual environment remains active. All pathing is automatically resolved to the repository root.

## Available Commands

### High-level Commands

* `ding init [directory]` - Initialize a new empty repository (creates the `.ding` hidden folder).
* `ding add <path>` - Hash a file or recursively hash a directory (e.g., `ding add .`) and update the staging index. Automatically handles file deletions.
* `ding commit -m "<message>"` - Snapshot the staging area and record a new commit.
* `ding log` - Traverse and print the commit history for the current branch.
* `ding branch <branch_name>` - Create a new branch pointing to the current commit.
* `ding checkout <branch_name>` - Switch branches. Uses tree-diffing to efficiently update the working directory and clean up zombie folders.

### Low-level Commands

* `ding hash-object <file>` - Hash a file, compress it, and safely store it in the object database.
* `ding cat-file <oid>` - Decompress and print the contents of a stored object.
* `ding write-tree` - Create a Merkle tree object from the current index.

## Example Workflow

```bash
# Initialize a new repository
ding init

# Create files and add everything to the staging area
echo "print('hello world')" > script.py
ding add .

# Commit the changes
ding commit -m "Initial commit"

# Check the history
ding log

# Create a new branch and switch to it
ding branch feature-test
ding checkout feature-test

```
