import ast
from typing import List, Dict


# Chunk size limits
MIN_CHUNK_SIZE = 50
MAX_CHUNK_SIZE = 1500


def extract_chunks_from_python(file_path: str, content: str) -> List[Dict]:
    """
    Python file se function aur class level pe chunks nikalo.
    """
    chunks = []

    try:
        tree = ast.parse(content)
        lines = content.split("\n")

        for node in ast.walk(tree):

            if isinstance(node, (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef
            )):

                start_line = node.lineno - 1
                end_line = node.end_lineno

                chunk_lines = lines[start_line:end_line]
                chunk_text = "\n".join(chunk_lines)

                # Small chunks skip karo
                if len(chunk_text.strip()) < MIN_CHUNK_SIZE:
                    continue

                # Large chunks trim karo
                if len(chunk_text) > MAX_CHUNK_SIZE:
                    chunk_text = chunk_text[:MAX_CHUNK_SIZE]

                chunks.append({
                    "content": chunk_text,
                    "metadata": {
                        "file_path": file_path,
                        "type": type(node).__name__,
                        "name": node.name,
                        "start_line": node.lineno,
                        "end_line": node.end_lineno
                    }
                })

    except SyntaxError as e:
        print(f"AST parse failed for {file_path}: {e}")
        chunks = fallback_chunking(file_path, content)

    return chunks


def fallback_chunking(file_path: str, content: str) -> List[Dict]:
    """
    Non-Python files ke liye simple chunking.
    """
    chunks = []

    chunk_size = 1000
    overlap = 100

    start = 0
    chunk_index = 0

    while start < len(content):

        end = start + chunk_size
        chunk_text = content[start:end]

        if len(chunk_text.strip()) > MIN_CHUNK_SIZE:

            chunks.append({
                "content": chunk_text,
                "metadata": {
                    "file_path": file_path,
                    "type": "chunk",
                    "name": f"chunk_{chunk_index}",
                    "start_char": start,
                    "end_char": end
                }
            })

        start = end - overlap
        chunk_index += 1

    return chunks


def chunk_files(extracted_files: List[Dict]) -> List[Dict]:
    """
    Saari extracted files ko chunk karo.
    """
    all_chunks = []

    for file in extracted_files:

        file_path = file["file_path"]
        content = file["content"]
        extension = file["extension"]

        if extension == ".py":
            chunks = extract_chunks_from_python(file_path, content)
        else:
            chunks = fallback_chunking(file_path, content)

        all_chunks.extend(chunks)

    print(f"Total chunks created: {len(all_chunks)}")

    return all_chunks


if __name__ == "__main__":

    import sys
    sys.path.append(".")

    from src.ingestion.repo_loader import extract_files

    REPO_PATH = "data/flask"

    files = extract_files(REPO_PATH)

    chunks = chunk_files(files)

    print("\n--- Sample Chunk ---")

    if chunks:

        sample = chunks[0]

        print(f"Name: {sample['metadata']['name']}")
        print(f"Type: {sample['metadata']['type']}")

        if "start_line" in sample["metadata"]:
            print(
                f"Lines: "
                f"{sample['metadata']['start_line']} - "
                f"{sample['metadata']['end_line']}"
            )

        print(f"Content preview:\n{sample['content'][:300]}")

    else:
        print("No chunks created.")