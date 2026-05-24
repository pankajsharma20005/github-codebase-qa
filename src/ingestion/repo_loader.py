import os
import shutil
from git import Repo
from typing import List, Dict

# Sirf yeh extensions chahiye
SUPPORTED_EXTENSIONS = [".py", ".js", ".ts", ".java", ".cpp", ".go", ".rs"]

# Yeh folders skip karo
SKIP_FOLDERS = [".git", "node_modules", "__pycache__", ".venv", "venv", ".idea"]


def clone_repo(repo_url: str, clone_path: str) -> str:
    """
    GitHub repo ko clone karo local machine pe.
    Agar pehle se exist karta hai toh delete karke fresh clone karo.
    """
    if os.path.exists(clone_path):
        print(f"Folder already exists — deleting: {clone_path}")
        shutil.rmtree(clone_path)

    print(f"Cloning repo: {repo_url}")
    Repo.clone_from(repo_url, clone_path)
    print(f"Clone complete: {clone_path}")
    return clone_path


def extract_files(repo_path: str) -> List[Dict]:
    """
    Cloned repo se saari supported code files nikalo.
    Har file ke liye return karo: file_path + content
    """
    extracted = []

    for folder, subfolders, files in os.walk(repo_path):

        # Unwanted folders skip karo
        subfolders[:] = [f for f in subfolders if f not in SKIP_FOLDERS]

        for file in files:
            # Sirf supported extensions
            if any(file.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                file_path = os.path.join(folder, file)

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # Empty files skip karo
                    if content.strip():
                        extracted.append({
                            "file_path": file_path,
                            "file_name": file,
                            "content": content,
                            "extension": os.path.splitext(file)[1]
                        })

                except Exception as e:
                    print(f"Could not read {file_path}: {e}")

    print(f"Total files extracted: {len(extracted)}")
    return extracted


if __name__ == "__main__":
    # Test karo
    REPO_URL = "https://github.com/pallets/flask"
    CLONE_PATH = "data/flask"

    clone_repo(REPO_URL, CLONE_PATH)
    files = extract_files(CLONE_PATH)

    # Pehli 3 files print karo
    for f in files[:3]:
        print(f"\n--- {f['file_name']} ---")
        print(f['content'][:200])