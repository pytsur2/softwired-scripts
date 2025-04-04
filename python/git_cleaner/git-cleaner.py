#!/usr/bin/env python3

import os
import shutil
import sys
import subprocess

def ensure_root():
    if os.geteuid() != 0:
        print(" Root privileges required, restarting with sudo...")
        try:
            subprocess.check_call(['sudo', sys.executable] + sys.argv)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to run with sudo: {e}")
        sys.exit()

def find_git_repos(start_path):
    git_dirs = []
    for root, dirs, files in os.walk(start_path):
        if ".git" in dirs:
            git_dirs.append(root)
            dirs[:] = []  # Do not recurse further into this directory
    return git_dirs

def remove_git_repo(repo_path):
    git_path = os.path.join(repo_path, ".git")
    try:
        shutil.rmtree(git_path)
        print(f"Removed: {git_path}")
    except PermissionError as e:
        print(f"❌ Permission error: {e}")
        print(" Tip: Check the file owner or try again as root.")
    except Exception as e:
        print(f"❌ Error while deleting: {e}")

if __name__ == "__main__":
    ensure_root()

    current_dir = os.getcwd()
    print(f"Searching from: {current_dir}\n")
    repos = find_git_repos(current_dir)

    if not repos:
        print("No Git repositories found.")
        sys.exit(0)

    print("Git repositories:\n")
    for i, path in enumerate(repos, 1):
        print(f"{i}. {path}")

    choice = input("\nEnter a number to remove the .git directory (Enter = skip): ").strip()
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(repos):
            confirm = input(f"Are you sure you want to delete the .git directory from: {repos[idx - 1]}? (y/n): ").lower()
            if confirm == 'y':
                remove_git_repo(repos[idx - 1])
            else:
                print("Deletion canceled.")
        else:
            print("⚠️ Invalid selection.")
    else:
        print("Exiting without deletion.")
