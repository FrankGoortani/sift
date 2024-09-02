import argparse
import sys
import os
from .generate_md import generate_markdown_files
from .config import load_config
import subprocess
import tempfile
import asyncio

def main():
    parser = argparse.ArgumentParser(
        description="Code Knowledge Graph Builder - A tool to generate knowledge graphs"
                    "from code repositories."
    )

    parser.add_argument(
        'repo_or_path',
        type=str,
        help="URL of the Git repository or path to a local directory"
             "containing the code"
    )

    parser.add_argument(
        'branch',
        type=str,
        nargs='?',
        default=None,
        help='(Optional) Branch name to checkout if providing a Git repository URL'
    )

    parser.add_argument(
        '--config',
        type=str,
        default="config.json",
        help='Path to the configuration file (default: config.json)'
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Determine if the input is a URL (assume it is if it contains "http" or "git")
    if "http" in args.repo_or_path or "git" in args.repo_or_path:
        with tempfile.TemporaryDirectory() as tmp_dir:
            print(f"Cloning repository {args.repo_or_path} into temporary directory...")
            clone_command = ["git", "clone", args.repo_or_path, tmp_dir]
            if args.branch:
                clone_command.extend(["-b", args.branch])

            result = subprocess.run(clone_command, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error cloning repository: {result.stderr}")
                sys.exit(1)
            print("Repository cloned successfully.")

            # Generate markdown files
            asyncio.run(generate_markdown_files(tmp_dir, config))
    else:
        # Handle as a local directory path
        if not os.path.isdir(args.repo_or_path):
            print(f"The provided path '{args.repo_or_path}' is not a valid directory.")
            sys.exit(1)

        # Generate markdown files
        asyncio.run(generate_markdown_files(args.repo_or_path, config))
