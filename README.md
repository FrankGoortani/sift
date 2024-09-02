# SIFT - Code Knowledge Graph Builder

## Overview

Code Knowledge Graph Builder is an experimental tool designed to construct a knowledge graph from a code repository. This tool analyzes the structure of the repository, identifies code APIs, patterns, anti-patterns, and dependencies, and generates Markdown files that summarize these findings. The system then aggregates these summaries, bubbling up the information through the directory hierarchy to create a comprehensive knowledge graph.

This knowledge graph can later be used as an AI-driven linting tool, capable of answering questions related to using, extending, and fixing the code.

## Features

- **Automatic Code Analysis**: Iterates through folders and files to identify APIs, patterns, anti-patterns, and dependencies.
- **Markdown Generation**: Creates detailed Markdown files in each folder, summarizing the findings for easy reference.
- **Hierarchical Summarization**: Aggregates and summarizes Markdown files from each folder, bubbling up the information to the parent folder.
- **Knowledge Graph Construction**: Establishes a knowledge graph from the generated Markdown files to provide insights and answers about the codebase.
- **Potential AI Linting Tool**: Can be extended to serve as an AI-driven linting tool for code analysis and improvement.

## Installation

Clone the repository and install the dependencies using [Poetry](https://python-poetry.org/):

```bash
git clone https://github.com/yourusername/code-knowledge-graph-builder.git
cd code-knowledge-graph-builder
poetry install
```

## Local Development

You will need to create a .env file in the root of the project with the following content:

```bash
OPENAI_API_KEY=your_openai_api_key
```

Following are a list of commands that can be used to develop the project locally:

### Linting

Run the linter to ensure the codebase is clean:

```bash
poetry run ruff check .

poetry run mypy . --namespace-packages --explicit-package-bases --show-traceback
```

### Running the CLI using

```bash
poetry run sift -- [folder path - or - repository path]
```

### cleanup

```bash
find . -type f -name '*.sift' -exec rm -v {} +
```

## Usage

1. Run the tool on your code repository:

   ```bash
   poetry run sift /path/to/your/repository
   ```

2. The tool will analyze the codebase, generate Markdown files, and summarize them in each folder.

3. View the generated Markdown files and navigate through the knowledge graph to understand the code structure, usage, and potential areas for improvement.

## Example

After running the tool, your repository might look something like this:

```text
your-repository/
│
├── src/
│   ├── __init__.py
│   ├── module1.py
│   ├── module2.py
│   ├── module1_summary.md
│   ├── module2_summary.md
│   └── src_summary.md
│
├── tests/
│   ├── test_module1.py
│   ├── test_module2.py
│   ├── test_module1_summary.md
│   ├── test_module2_summary.md
│   └── tests_summary.md
│
└── repository_summary.md
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix (`git checkout -b feature-name`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Plans

- Integration with AI models for advanced linting and code quality assessment.
- Improved pattern recognition and summarization algorithms.
- Enhanced support for various programming languages.

---

*Note: This project is in an experimental phase and is subject to significant changes as development progresses.*
