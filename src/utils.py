
def word_count(string):
    return len(string.split())

# split a content into chunks based on # of words in each chunk
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
