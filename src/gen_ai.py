# gen_ai.py
import openai
import os
from dotenv import load_dotenv
from .utils import split_file_content

load_dotenv()

client = openai.AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

async def generate_text_from_prompt(prompt, content_chunk, config):
    """Generates a markdown text using the OpenAI API based on the provided prompt."""
    response = await client.chat.completions.create(
        model=config["default_model"],
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content_chunk}
        ]
    )
    return response.choices[0].message.content

async def process_large_file(prompt, content, config):
    """Handles large files by splitting them and processing each chunk."""
    chunks = split_file_content(content, config["max_tokens"], config["token_split_overlap"])
    results = [await generate_text_from_prompt(prompt, chunk, config) for chunk in chunks]
    return "\n".join(results)
