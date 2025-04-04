# git-cleaner

This is a simple Python script that helps you locate and remove unwanted `.git` folders from a directory tree. Useful for situations where you want to clean up nested Git repositories before archiving, sharing, or publishing a project.

## Features

- Recursively searches for `.git` folders from the current directory
- Lists all detected Git repositories
- Allows selective deletion with confirmation
- Requires `sudo` to safely handle permissions

## Usage

```bash
sudo python3 git-cleaner.py
```