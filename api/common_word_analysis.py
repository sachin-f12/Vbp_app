import os
import logging
import re
import fitz  # PyMuPDF
import ast
import asyncio
from pathlib import Path
from typing import List, Dict
from fastapi import APIRouter, FastAPI, HTTPException, Query
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
from utils.run_analysis import run_openai_finding_keywords_for_search
from services.pubmed import fetch_pubmed_results
from services.google_scholar import fetch_google_scholar_results
from utils.search_utils import download_google_scholar_pdf
from utils.pubmed_utils import download_pdf
from utils.file_operations import rename_downloaded_files

# Load environment variables
load_dotenv(override=True)
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
router = APIRouter()
app = FastAPI()

BASE_DIR = Path("download")

# Function to get categories dynamically
def get_categories(source: str):
    source_path = BASE_DIR / source
    return {d.name: d.name for d in source_path.iterdir() if d.is_dir()} if source_path.exists() else {}

@router.get("/fetch-folder-structure")
def fetch_folder_structure(source: str = Query(..., enum=["Scholar", "pubmed"])):
    categories = get_categories(source)
    if not categories:
        raise HTTPException(status_code=404, detail="No categories found")
    return {"source": source, "categories": list(categories.keys())}

@router.get("/fetch-articles")
def fetch_articles(source: str = Query(..., enum=["Scholar", "pubmed"]), categories: List[str] = Query(...)):
    selected_pdfs = {}
    for category in categories:
        category_path = BASE_DIR / source / category
        if category_path.exists():
            pdf_files = [f.name for f in category_path.iterdir() if f.suffix == ".pdf"]
            selected_pdfs[category] = pdf_files
    if not selected_pdfs:
        raise HTTPException(status_code=404, detail="No PDFs found")
    return {"source": source, "selected_categories": selected_pdfs}

# Function to extract text from PDF in chunks
def extract_text_in_chunks(pdf_path: Path, chunk_size: int = 14999) -> List[str]:
    text = ""
    chunks = []
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + " "
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading PDF {pdf_path.name}: {str(e)}")
    return chunks

# Function to convert OpenAI output to a Python list
def string_to_python_list(string):
    cleaned_string = re.sub(r'```(?:python)?|```', '', string).strip()
    list_match = re.search(r'\[.*\]', cleaned_string, re.DOTALL)
    return ast.literal_eval(list_match.group()) if list_match else []

# Function to truncate text to fit OpenAI's token limit
def truncate_text_to_fit_token_limit(text: str, max_tokens: int = 15000) -> str:
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = enc.encode(text)
    logging.info(f"Original token count: {len(tokens)}")
    if len(tokens) > max_tokens:
        truncated_tokens = tokens[:max_tokens]
        truncated_text = enc.decode(truncated_tokens)
        logging.info(f"Truncated token count: {len(truncated_tokens)}")
        return truncated_text
    return text

@router.post("/analyze-common-words")
def analyze_common_words(
    source: str = Query(..., enum=["Scholar", "pubmed"]),
    categories: List[str] = Query(...),
    pdfs: List[str] = Query(...),
    num_matches: int = Query(10, ge=1, le=100)
):
    """Analyze selected PDFs for technical keywords and search queries."""
    all_keywords = []
    for category in categories:
        pdf_dir = BASE_DIR / source / category
        for pdf in pdfs:
            pdf_path = pdf_dir / pdf
            if not pdf_path.exists():
                raise HTTPException(status_code=404, detail=f"PDF not found: {pdf}")
            text_chunks = extract_text_in_chunks(pdf_path, chunk_size=5000)
            for chunk in text_chunks:
                truncated_text = truncate_text_to_fit_token_limit(chunk, max_tokens=3000)
                raw_output = run_openai_finding_keywords_for_search(truncated_text)
                common_words = string_to_python_list(raw_output)
                all_keywords.extend(common_words)
    unique_keywords = list(set(all_keywords))[:num_matches]
    return {"common_words": unique_keywords}

@router.get("/analyse_common_words")
async def search_articles(
    search_terms: List[str] = Query(...),
    search_source: str = Query("Google Scholar", enum=["Google Scholar", "PubMed"]),
    max_results: int = Query(10, ge=1, le=100)
):
    """Fetch articles based on analyzed common words."""
    if not search_terms:
        raise HTTPException(status_code=400, detail="At least one search term is required.")
    selected_term = search_terms[0]
    folder_path = Path("common_word_analysis") / selected_term
    folder_path.mkdir(parents=True, exist_ok=True)
    results = {"google_scholar": [], "pubmed": [], "stored_pdfs": []}
    if search_source == "Google Scholar":
        google_scholar_results = await fetch_google_scholar_results(search_terms, max_results)
        google_scholar_pdfs = [download_google_scholar_pdf(url, selected_term, "Google Scholar") for url in google_scholar_results]
        rename_downloaded_files(selected_term, "Google Scholar")
        results.update({"google_scholar": google_scholar_results, "stored_pdfs": google_scholar_pdfs})
    elif search_source == "PubMed":
        pubmed_results = await fetch_pubmed_results(search_terms, max_results)
        pubmed_pdfs = [download_pdf(pmcid, selected_term, "PubMed") for pmcid in pubmed_results]
        rename_downloaded_files(selected_term, "PubMed")
        results.update({"pubmed": pubmed_results, "stored_pdfs": pubmed_pdfs})
    return results
