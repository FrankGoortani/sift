import git
from datetime import datetime
import os

def word_count(string):
    """
    Counts the number of words in a string.

    :param string: The input string.
    :return: The number of words in the string.
    """
    return len(string.split())

def split_file_content(content, max_length=80000, overlap=500):
    """
    Splits the content of a file into chunks based on the number of words in each chunk.

    :param content: The content of the file.
    :param max_length: The maximum number of words in each chunk (default is 80000).
    :param overlap: The number of overlapping words between consecutive chunks
                    (default is 500).
    :return: A list of chunks.
    """
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

def get_latest_git_hash(folder_path):
    """
    Extracts the latest Git commit hash for the repository.

    :param folder_path: Path to the Git repository.
    :return: Latest commit hash as a string.
    """
    repo = git.Repo(folder_path)
    return repo.head.object.hexsha

def generate_file_address(file_path):
    """
    Generates a string showing the file address and name.

    :param file_path: Path to the file.
    :return: Formatted string representing the file address and name.
    """
    return f"# File summary: {file_path}"

def generate_file_summary_md(file_path, summary, git_hash):
    """
    Generates the markdown content for a file summary.

    :param file_path: Path to the file being summarized.
    :param summary: AI-generated summary for the file.
    :param git_hash: Latest commit hash for the repository.
    :return: Formatted markdown content as a string.
    """
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
    """
    Generates the markdown content for a folder summary.

    :param folder_path: Path to the folder being summarized.
    :param files_and_folders: List of files and subfolders in the folder.
    :param summary: AI-generated summary for the folder.
    :param git_hash: Latest commit hash for the repository.
    :return: Formatted markdown content as a string.
    """
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

def load_gitignore_patterns(repo_path, config):
    """
    Loads the .gitignore patterns and combines them with default exclusions.

    :param repo_path: Path to the repository root.
    :param config: Configuration dictionary with default exclusions.
    :return: Set of exclusion patterns.
    """
    gitignore_path = os.path.join(repo_path, ".gitignore")
    patterns = set(config.get("default_exclusions", []))

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as gitignore_file:
            for line in gitignore_file:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.add(line)

    return patterns

def should_exclude(path, patterns):
    """
    Checks if a given path matches any exclusion patterns.

    :param path: Path to check.
    :param patterns: Set of exclusion patterns.
    :return: True if the path should be excluded, False otherwise.
    """
    for pattern in patterns:
        if pattern in path:
            return True
    return False
