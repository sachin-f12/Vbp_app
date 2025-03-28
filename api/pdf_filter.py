from fastapi import FastAPI, HTTPException, Query,APIRouter
from pathlib import Path
import shutil
import fitz  # PyMuPDF
from typing import List, Optional
import os 
router = APIRouter()

INPUT_DIR = "download"  # Set your base input directory
OUTPUT_DIR = r"download\filtered_pdfs"  # Set output directory for filtered PDFs

def list_all_directories(base_path: str):
    """ Recursively lists all directories and subdirectories. """
    path = Path(base_path)
    all_dirs = []

    for folder in path.rglob("*"):
        if folder.is_dir():
            all_dirs.append(str(folder))  # Convert Path to string

    return all_dirs


def extract_text_from_pdf(pdf_file: Path) -> str:
    """Extracts text from a PDF file."""
    text = ""
    with fitz.open(str(pdf_file)) as doc:
        for page in doc:
            text += page.get_text()
    return text.lower()


def search_terms_in_text(text: str, include_terms: List[str], exclude_terms: List[str], any_terms: List[str]) -> bool:
    """Checks if a text satisfies AND, NOT, and OR conditions."""
    include_pass = all(term.lower() in text for term in include_terms)
    exclude_pass = not any(term.lower() in text for term in exclude_terms)
    or_pass = any(term.lower() in text for term in any_terms) if any_terms else True
    return include_pass and exclude_pass and or_pass


@router.get("/list-all-directories")
def get_all_directories():
    """ Returns all directories and subdirectories under INPUT_DIR. """
    return {"directories": list_all_directories(INPUT_DIR)}

@router.post("/filter-pdfs")
def filter_pdfs(
    src_directory: str,
    include_terms: Optional[List[str]] = Query(default=[]),
    exclude_terms: Optional[List[str]] = Query(default=[]),
    any_terms: Optional[List[str]] = Query(default=[]),
):
    """Filters PDFs based on search terms and copies matching files to OUTPUT_DIR."""
    src_path = Path(src_directory)
    dest_path = Path(OUTPUT_DIR) / f"filtered_results_include-{'_'.join(include_terms)}_exclude-{'_'.join(exclude_terms)}_any-{'_'.join(any_terms)}"
    dest_path.mkdir(parents=True, exist_ok=True)
    
    if not src_path.exists() or not src_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid source directory")
    
    pdf_files = list(src_path.rglob("*.pdf"))
    matched_files = 0
    
    for pdf_file in pdf_files:
        text = extract_text_from_pdf(pdf_file)
        if search_terms_in_text(text, include_terms, exclude_terms, any_terms):
            shutil.copy(str(pdf_file), str(dest_path / pdf_file.name))
            matched_files += 1
    
    return {"message": "Filtering complete", "matched_files": matched_files, "output_directory": str(dest_path)}
