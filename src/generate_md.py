import os
from .gen_ai import process_large_file, generate_text_from_prompt
from .prompts import CODE_PROMPT, CONFIG_PROMPT, DOC_PROMPT, FOLDER_SUMMARY_PROMPT
from .utils import word_count, get_latest_git_hash, generate_file_summary_md, generate_folder_summary_md, extract_git_hash_from_md

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

async def generate_file_summary(file_path, file_type, content, config, git_hash):
    # Determine the markdown file path
    markdown_file_path = f"{os.path.splitext(file_path)[0]}{config['sift_extension']}"

    # Check if the markdown file already exists and has the same Git hash
    existing_hash = extract_git_hash_from_md(markdown_file_path)
    if existing_hash == git_hash:
        print(f"Skipping {file_path} as the content has not changed (Git hash: {git_hash}).")
        return markdown_file_path, None

    # Generate markdown content based on file type and content size
    if word_count(content) > config["max_tokens"]:
        if file_type == 'code':
            prompt = CODE_PROMPT
        elif file_type == 'config':
            prompt = CONFIG_PROMPT
        elif file_type == 'documentation':
            prompt = DOC_PROMPT
        markdown_content = await process_large_file(prompt, content)
    else:
        if file_type == 'code':
            prompt = CODE_PROMPT
        elif file_type == 'config':
            prompt = CONFIG_PROMPT
        elif file_type == 'documentation':
            prompt = DOC_PROMPT
        markdown_content = await generate_text_from_prompt(prompt, content, config)

    # Generate the file summary markdown content
    file_md_content = generate_file_summary_md(file_path, markdown_content, git_hash)

    # Save the summary as a markdown file
    with open(markdown_file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(file_md_content)

    return markdown_file_path, markdown_content

async def generate_folder_summary(root, folder_markdown_content, config, git_hash):
    folder_name = os.path.basename(root)
    folder_summary_path = os.path.join(root, f"{folder_name}_folder{config['sift_extension']}")

    # Check if the folder summary file already exists and has the same Git hash
    existing_hash = extract_git_hash_from_md(folder_summary_path)
    if existing_hash == git_hash:
        print(f"Skipping folder {root} as the content has not changed (Git hash: {git_hash}).")
        return folder_summary_path, None

    full_markdown_content = "\n\n".join(folder_markdown_content)
    # Generate summary for the folder
    folder_summary = await generate_text_from_prompt(FOLDER_SUMMARY_PROMPT, full_markdown_content, config)

    # Generate files_and_folders: List of files and subfolders in the folder.
    files_and_folders = os.listdir(root)

    # Generate the folder summary markdown content
    folder_md_content = generate_folder_summary_md(root, files_and_folders, folder_summary, git_hash)

    # Save the folder summary as a markdown file at the folder level
    with open(folder_summary_path, 'w', encoding='utf-8') as folder_md_file:
        folder_md_file.write(folder_md_content)

    return folder_summary_path, folder_md_content

async def generate_markdown_files(start_path, config):
    parent_folder_markdown_files = []
    parent_folder_markdown_content = []
    print(f"Generating markdown files for {start_path}")
    git_hash = get_latest_git_hash(start_path)

    for root, dirs, files in os.walk(start_path, topdown=True):
        folder_markdown_files = []
        folder_markdown_content = []

        for file in files:
            print(f"Processing file: {file}")
            file_path = os.path.join(root, file)
            # If file ends with config["sift_extension"], skip it
            if file.endswith(config["sift_extension"]):
                print(f"Skipping file {file} as it is a generated summary file.")
                continue

            file_type = categorize_file(file_path, config)

            if file_type is None:
                print(f"Skipping file {file} as it is not a code, config, or documentation file.")
                continue  # Skip non-relevant files

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            markdown_file_path, markdown_content = await generate_file_summary(file_path, file_type, content, config, git_hash)

            # Collect markdown file paths and content for the folder summary
            if markdown_content:  # Only add if the content was generated (not skipped)
                folder_markdown_files.append(markdown_file_path)
                folder_markdown_content.append(markdown_content)

        # Generate folder-level summary after processing all files
        folder_summary_path, folder_summary = await generate_folder_summary(root, folder_markdown_content, config, git_hash)

        # Store folder summaries for the parent folder
        if folder_summary:  # Only add if the content was generated (not skipped)
            parent_folder_markdown_files.append(folder_summary_path)
            parent_folder_markdown_content.append(folder_summary)

        # If we're exiting a folder, generate the parent folder summary
        if not dirs:
            if parent_folder_markdown_files:
                await generate_folder_summary(root, parent_folder_markdown_content, config, git_hash)
                parent_folder_markdown_files.clear()
                parent_folder_markdown_content.clear()
