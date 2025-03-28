import os
import requests
import logging
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
OUTPUT_DIR = Path("download/Scholar")# Ensure absolute path
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
CHUNK_SIZE = 1024
RETRIES = 3
BACKOFF_FACTOR = 0.3

def search_google_scholar(keyword, start=0):
    """Searches Google Scholar using SerpAPI."""
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_scholar",
        "q": keyword,
        "api_key": os.getenv("SERP_API_KEY"),
        "start": start
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error in search_google_scholar: {e}")
        return None

def extract_pdf_links(data):
    """Extracts PDF links from search results."""
    links = []
    if not data or "organic_results" not in data:
        logging.warning("No organic results found in data")
        return links
        
    for result in data.get("organic_results", []):
        for resource in result.get("resources", []):
            if resource.get("file_format") == "PDF":
                links.append(resource["link"])
    
    logging.info(f"Extracted {len(links)} PDF links")
    return links
import re
def sanitize_filename(filename, max_length=200):
    """Sanitizes filenames by removing invalid characters and ensuring a valid length."""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename).strip()

    if not filename:
        return "default"  # ✅ No .pdf for folder names

    name, ext = os.path.splitext(filename)

    if len(name) > max_length - len(ext):
        name = name[:max_length - len(ext)]

    return f"{name}{ext}" if ext else f"{name}"  # ✅ Remove .pdf for folder names

from utils.file_operations import rename_downloaded_files  # Import the rename function

def download_google_scholar_pdf(pdf_url, search_term, search_source="Google Scholar"):
    """Downloads the PDF and stores it in the correct directory based on the search term."""

    safe_search_term = sanitize_filename(search_term).replace(".pdf", "")

    if search_source == "BOTH":
        output_dir = Path(f"download/Both/Scholar/{safe_search_term}")
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = Path(f"download/Scholar/{safe_search_term}")
        os.makedirs(output_dir, exist_ok=True)


    pdf_filename = sanitize_filename(pdf_url.split("/")[-1].split("?")[0])
    pdf_path = output_dir / pdf_filename

    if pdf_path.exists() and pdf_path.stat().st_size > 1000:
        logging.info(f"PDF already exists: {pdf_path}")
        return str(pdf_path)

    try:
        headers = {'User-Agent': USER_AGENT, 'Accept': 'application/pdf'}
        response = requests.get(pdf_url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        with open(pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

        if pdf_path.stat().st_size < 1000:
            pdf_path.unlink()
            logging.error(f"Downloaded file too small: {pdf_url}")
            return None

        logging.info(f"Successfully downloaded PDF: {pdf_path}")

        # 🛠 Rename after successful download
        # rename_downloaded_files(search_term, search_source)  

        return str(pdf_path)

    except Exception as e:
        logging.error(f"Failed to download PDF: {pdf_url}, Error: {e}")
        return None
