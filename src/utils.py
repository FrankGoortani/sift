import git
from datetime import datetime
import os
import fnmatch

def word_count(string):
    return len(string.split())

def split_file_content(content, max_length=80000, overlap=500):
    words = content.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += 1

        if current_length >= max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0

        if current_length > overlap:
            current_chunk = current_chunk[-overlap:]
            current_length = overlap

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def get_latest_git_hash(path):
    """
    Extracts the latest Git commit hash for a file or folder.

    :param path: Path to the file or folder.
    :return: Latest commit hash as a string, or 'No commits found' if none are found.
    """
    try:
        repo = git.Repo(os.path.dirname(path) if os.path.isfile(path) else path, search_parent_directories=True)
        latest_commit = repo.iter_commits(paths=path, max_count=1)
        return next(latest_commit).hexsha
    except StopIteration:
        return 'No commits found'  # Return a default value if no commits are found
    except Exception as e:
        print(f"Error accessing Git history for {path}: {e}")
        return 'Error fetching commit hash'

def generate_file_address(file_path):
    return f"# File summary: {file_path}"

def generate_file_summary_md(file_path, summary, git_hash):
    print(f"wrapping up summary for {file_path}")
    file_address = generate_file_address(file_path)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_content = f"""
{file_address}
## Version
{git_hash}
{timestamp}
## AI Summary
{summary}
    """
    return md_content.strip()

def generate_folder_summary_md(folder_path, files_and_folders, summary, git_hash):
    print(f"wrapping up summary for {folder_path}")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    files_and_folders_list = "\n".join([f"- {item}" for item in files_and_folders])

    md_content = f"""
# Folder summary: {folder_path}
## Files and Sub-folders
{files_and_folders_list}
## Version
{git_hash}
{timestamp}
## AI Summary
{summary}
    """
    return md_content.strip()

def load_gitignore_patterns(repo_path, config):
    gitignore_path = os.path.join(repo_path, ".gitignore")
    patterns = set(config["default_exclusions"])

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as gitignore_file:
            for line in gitignore_file:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.add(line)

    return patterns

def should_exclude(path, patterns):
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, f"*/{pattern}"):
            return True
    return False

def extract_git_hash_from_md(file_path):
    """Extracts the Git hash from an existing markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as md_file:
            for line in md_file:
                if line.startswith("## version"):
                    next_line = next(md_file).strip()  # Get the line after '## version'
                    return next_line  # This is the Git hash
    except FileNotFoundError:
        return None
