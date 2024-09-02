import os
from datetime import datetime
from .gen_ai import process_large_file, generate_text_from_prompt
from .prompts import CODE_PROMPT, CONFIG_PROMPT, DOC_PROMPT, FOLDER_SUMMARY_PROMPT
from .utils import (
    word_count,
    get_latest_git_hash,
    generate_file_summary_md,
    generate_folder_summary_md,
    extract_git_hash_from_md,
    load_gitignore_patterns,
    should_exclude,
)

def is_code_file(file_path, code_extensions):
    return file_path.endswith(tuple(code_extensions))

def is_config_file(file_path, config_extensions):
    return file_path.endswith(tuple(config_extensions))

def is_documentation_file(file_path, documentation_extensions):
    return file_path.endswith(tuple(documentation_extensions))

def categorize_file(file_path, config):
    if is_code_file(file_path, config["code_extensions"]):
        return 'code'
    elif is_config_file(file_path, config["config_extensions"]):
        return 'config'
    elif is_documentation_file(file_path, config["documentation_extensions"]):
        return 'documentation'
    else:
        return None

async def generate_file_summary(file_path, file_type, content, config):
    git_hash = get_latest_git_hash(file_path)
    print(f"Generating summary for {file_path}")
    # Extract existing hash code from sift file to avoid rerunning if unchanged
    # existing_hash = extract_git_hash_from_md(f"{os.path.splitext(file_path)[0]}{config['sift_extension']}")
    # if existing_hash == git_hash:
    #     print(f"Skipping {file_path} as the content has not changed (Git hash: {git_hash}).")
    #     return git_hash, None

    if file_type == 'code':
        prompt = CODE_PROMPT
    elif file_type == 'config':
        prompt = CONFIG_PROMPT
    elif file_type == 'documentation':
        prompt = DOC_PROMPT

    if word_count(content) > config["max_tokens"]:
        markdown_content = await process_large_file(prompt, content, config)
    else:
        markdown_content = await generate_text_from_prompt(prompt, content, config)

    file_md_content = generate_file_summary_md(file_path, markdown_content, git_hash)
    return git_hash, file_md_content

async def generate_folder_summary(root, files_and_dirs, config):
    folder_name = os.path.basename(root)
    print(f"Generating folder summary for {folder_name}")
    sift_file_path = os.path.join(root, f"{config['sift_extension']}")
    folder_git_hash = get_latest_git_hash(root)
    folder_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    folder_summary = f"# Folder Summary {root}\n\n## version\n{folder_git_hash}\n{folder_timestamp}\n\n"

    subfolder_summaries = []

    for item in sorted(files_and_dirs):
        item_path = os.path.join(root, item)

        # Process subfolders first
        if os.path.isdir(item_path):
            subfolder_summary_path = await generate_folder_summary(item_path, os.listdir(item_path), config)
            if subfolder_summary_path:
                with open(subfolder_summary_path, 'r', encoding='utf-8') as f:
                    subfolder_summary = f.read()
                    subfolder_summaries.append(subfolder_summary)
                    folder_summary += f"### {item}\n#### version\n{get_latest_git_hash(item_path)}\n\n#### knowledge graph\n\n"

    # Include subfolder summaries in the parent folder summary
    if subfolder_summaries:
        folder_summary += "\n".join(subfolder_summaries)

    # Process files in the current folder
    for item in files_and_dirs:
        item_path = os.path.join(root, item)
        print(f"Processing {item_path}")

        if os.path.isfile(item_path):
            file_type = categorize_file(item_path, config)
            if file_type is not None:
                with open(item_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                item_git_hash, markdown_content = await generate_file_summary(item_path, file_type, content, config)
                if markdown_content:
                    folder_summary += f"### {item}\n#### version\n{item_git_hash}\n\n#### knowledge graph\n{markdown_content}\n\n"

    # Generate folder-level AI summary
    folder_ai_summary = await generate_text_from_prompt(FOLDER_SUMMARY_PROMPT, folder_summary, config)
    folder_md_content = generate_folder_summary_md(root, files_and_dirs, folder_ai_summary, folder_git_hash)

    # Save the folder summary as a .sift file
    with open(sift_file_path, 'w', encoding='utf-8') as sift_file:
        sift_file.write(folder_md_content.strip())

    return sift_file_path

async def generate_markdown_files(start_path, config):
    exclusion_patterns = load_gitignore_patterns(start_path, config)

    for root, dirs, files in os.walk(start_path, topdown=False):  # Depth-first: subfolders first
        # Exclude directories that start with a dot in their path

        # Exclude directories that start with a dot in their path
        dirs[:] = [d for d in dirs if not os.path.join(root, d).startswith(os.path.join(start_path, '.'))]

        # Apply exclusion patterns
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclusion_patterns)]

        # Exclude files that start with a dot in their path
        files = [f for f in files if not os.path.join(root, f).startswith(os.path.join(start_path, '.'))]

        # Apply exclusion patterns
        files = [f for f in files if not should_exclude(os.path.join(root, f), exclusion_patterns)]

        # if root path does not contain any folders that starts with '.' and does not match any exclusion patterns
        folders = root.split('/')
        if not any(folder.startswith('.') for folder in folders) and not should_exclude(root, exclusion_patterns):
            print(f"Processing dirs in {root}: {dirs}")
            # Generate a folder-level sift file summarizing all files and subfolders
            await generate_folder_summary(root, dirs + files, config)
