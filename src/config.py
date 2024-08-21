import json
import os

def load_config(config_file_path="config.json", repo_path=None, args=None):
    # 1. Load defaults from the config.json in the root folder
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)

    # 2. Check the root folder of the repo or the folder submitted as the starting configurations
    if repo_path:
        repo_config_path = os.path.join(repo_path, "sift_config.json")
        if os.path.exists(repo_config_path):
            with open(repo_config_path, 'r') as repo_config_file:
                repo_config = json.load(repo_config_file)
                config.update(repo_config)  # Overwrite defaults with repo-specific configs

    # 3. Load any config passed with the args and overwrite the list
    if args:
        for key, value in vars(args).items():
            if value is not None:
                config[key] = value

    return config
