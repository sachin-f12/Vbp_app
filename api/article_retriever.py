from fastapi import APIRouter, HTTPException, Query

from services.google_scholar import fetch_google_scholar_results
from services.pubmed import fetch_pubmed_results
router = APIRouter()
@router.get("/search")
async def search_articles(
    search_terms: list[str] = Query(None, description="List of search terms"),
    search_source: str = Query("BOTH", enum=["Google Scholar", "PubMed", "BOTH"]),
    max_results: int = Query(10, ge=1, le=100)
):
    try:
        results = {"google_scholar": [], "pubmed": []}

        if search_source == "BOTH":
            half_results = max_results // 2
            google_scholar_results = await fetch_google_scholar_results(search_terms, half_results + (max_results % 2))
            pubmed_results = await fetch_pubmed_results(search_terms, half_results)
            results["google_scholar"] = google_scholar_results
            results["pubmed"] = pubmed_results
        elif search_source == "Google Scholar":
            results["google_scholar"] = await fetch_google_scholar_results(search_terms, max_results)
        elif search_source == "PubMed":
            results["pubmed"] = await fetch_pubmed_results(search_terms, max_results)

        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
