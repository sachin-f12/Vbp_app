from fastapi import APIRouter, HTTPException
import os
import json
import shutil
import zipfile
import io

router = APIRouter()

# Directory paths
BASE_DIR = "downloaded_articles"
GOOGLE_SCHOLAR_DIR = os.path.join(BASE_DIR, "Google_Scholar")
PUBMED_DIR = os.path.join(BASE_DIR, "PubMed")
BOTH_DIR = os.path.join(BASE_DIR, "Both")
STATUS_FILE = "article_status.json"

# Ensure directories exist
os.makedirs(GOOGLE_SCHOLAR_DIR, exist_ok=True)
os.makedirs(PUBMED_DIR, exist_ok=True)
os.makedirs(BOTH_DIR, exist_ok=True)

# Load & Save Article Status
def load_article_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_article_status(status_data):
    with open(STATUS_FILE, "w") as f:
        json.dump(status_data, f, indent=4)

article_status = load_article_status()

def store_downloaded_file(filename: str, source: str, search_term: str = ""):
    """
    Stores downloaded files automatically in the correct folder.
    - Google Scholar ➝ `downloaded_articles/Google_Scholar/`
    - PubMed ➝ `downloaded_articles/PubMed/`
    - Both ➝ `downloaded_articles/Both/{search_term}/`
    """
    if source == "Google_Scholar":
        folder = GOOGLE_SCHOLAR_DIR
    elif source == "PubMed":
        folder = PUBMED_DIR
    elif source == "Both":
        folder = os.path.join(BOTH_DIR, search_term.replace(" ", "_"))
        os.makedirs(folder, exist_ok=True)
    else:
        raise ValueError("Invalid source. Choose 'Google_Scholar', 'PubMed', or 'Both'.")

    # Simulate file move (In real case, move from temp download location)
    temp_path = os.path.join("temp_downloads", filename)  # Temporary download folder
    dest_path = os.path.join(folder, filename)

    if not os.path.exists(temp_path):
        raise FileNotFoundError(f"File {filename} not found in temporary download location!")

    shutil.move(temp_path, dest_path)
    print(f"✅ File '{filename}' moved to {folder}")

    return {"message": "File stored successfully", "file": filename, "stored_in": folder}

@router.get("/list-files/")
def list_files():
    """Lists all stored files."""
    files = []
    for root, _, filenames in os.walk(BASE_DIR):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(root, filename), BASE_DIR))
    
    return {"files": files}
