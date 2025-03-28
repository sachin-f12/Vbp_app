from fastapi import APIRouter, HTTPException, Query
from services.pubmed import fetch_pubmed_results
from services.google_scholar import fetch_google_scholar_results
from utils.search_utils import download_google_scholar_pdf
from utils.pubmed_utils import download_pdf
from utils.file_operations import rename_downloaded_files
import os
import json
from enum import Enum

router = APIRouter()

RECENT_SEARCHES_FILE = "recent_searches.json"

# Function to load recent searches
def load_recent_searches():
    if os.path.exists(RECENT_SEARCHES_FILE):
        with open(RECENT_SEARCHES_FILE, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict) and "recent_searches" in data:
                    return data["recent_searches"]
            except json.JSONDecodeError:
                return []
    return []

# Function to save recent searches
def save_recent_search(search_data):
    recent_searches = load_recent_searches()

    # Remove duplicates
    recent_searches = [s for s in recent_searches if s.get("search_terms") != search_data["search_terms"]]
    
    # Append new search and limit to last 10
    recent_searches.insert(0, search_data)
    recent_searches = recent_searches[:10]

    with open(RECENT_SEARCHES_FILE, "w") as f:
        json.dump({"recent_searches": recent_searches}, f, indent=4)

@router.get("/recent-searches")
def get_recent_searches():
    """Endpoint to retrieve recent searches."""
    return {"recent_searches": load_recent_searches()}

@router.get("/search")
async def search_articles(
    search_terms: list[str] = Query(None, description="List of search terms"),
    search_operator: str = Query("AND", enum=["AND", "OR"], description="Search operation mode"),
    search_source: str = Query("Google Scholar", enum=["Google Scholar", "PubMed"]),
    max_results: int = Query(10, ge=1, le=100)
):
    try:
        if not search_terms:
            raise HTTPException(status_code=400, detail="At least one search term is required.")

        combined_search_term = f" {search_operator} ".join(search_terms)
        selected_term = combined_search_term  # Store for folder naming

        search_data = {
            "search_terms": search_terms,
            "search_operator": search_operator,
            "search_source": search_source,
            "max_results": max_results
        }
        save_recent_search(search_data)

        results = {"google_scholar": [], "pubmed": [], "stored_pdfs": []}

        if search_source == "Google Scholar":
            google_scholar_results = await fetch_google_scholar_results([combined_search_term], max_results)
            google_scholar_pdfs = [download_google_scholar_pdf(url, selected_term, search_source="Google Scholar") for url in google_scholar_results]
            rename_downloaded_files(selected_term, "Google Scholar")
            results.update({"google_scholar": google_scholar_results, "stored_pdfs": google_scholar_pdfs})
        
        elif search_source == "PubMed":
            pubmed_results = await fetch_pubmed_results([combined_search_term], max_results)
            pubmed_pdfs = [download_pdf(pmcid, selected_term, search_source="PubMed") for pmcid in pubmed_results]
            rename_downloaded_files(selected_term, "PubMed")
            results.update({"pubmed": pubmed_results, "stored_pdfs": pubmed_pdfs})
        
        return results  

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
