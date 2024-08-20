import os
from .gen_ai import process_large_file, generate_text_from_prompt
from .prompts import CODE_PROMPT, CONFIG_PROMPT, DOC_PROMPT
from .utils import word_count

def is_code_file(file_path):
    # Define file extensions for code files
    return file_path.endswith(('.py', '.js', '.java', '.cpp', '.c', '.rb', '.go', '.ts', '.cs'))

def is_config_file(file_path):
    # Define file extensions for config files
    return file_path.endswith(('.json', '.yaml', '.yml', '.ini', '.env', '.cfg'))

def is_documentation_file(file_path):
    # Define file extensions for documentation files
    return file_path.endswith(('.md', '.rst', '.txt'))

def categorize_file(file_path):
    if is_code_file(file_path):
        return 'code'
    elif is_config_file(file_path):
        return 'config'
    elif is_documentation_file(file_path):
        return 'documentation'
    else:
        return None

async def generate_markdown_files(start_path, config):
    """
    Generate markdown files from the code in the specified repository or directory path.

    Args:
        start_path (str): URL of the Git repository or path to a local directory containing the code
        config (dict): Configuration dictionary

    Returns:
        None
    """
    for root, _, files in os.walk(start_path):
        for file in files:
            print(f"Processing file: {file}")
            file_path = os.path.join(root, file)
            file_type = categorize_file(file_path)

            if file_type is None:
                continue  # Skip non-relevant files

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if word_count(content) > 80000:  # Check if the file exceeds the context window
                if file_type == 'code':
                    prompt = CODE_PROMPT
                elif file_type == 'config':
                    prompt = CONFIG_PROMPT
                elif file_type == 'documentation':
                    prompt = DOC_PROMPT

                markdown_content = await process_large_file(prompt, content)
                print("Got large file content processed")
            else:
                if file_type == 'code':
                    prompt = CODE_PROMPT
                elif file_type == 'config':
                    prompt = CONFIG_PROMPT
                elif file_type == 'documentation':
                    prompt = DOC_PROMPT

                markdown_content = await generate_text_from_prompt(prompt, content)
                print("Got small file content processed")

            # Save the generated markdown to a file
            markdown_file_path = os.path.join(root, f"{os.path.splitext(file)[0]}_summary.md")
            with open(markdown_file_path, 'w', encoding='utf-8') as md_file:
                md_file.write(markdown_content)
