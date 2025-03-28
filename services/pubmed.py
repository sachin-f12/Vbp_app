import os
from utils.pubmed_utils import search_pubmed, extract_pmcids, download_pdf

async def fetch_pubmed_results(search_terms: list[str], max_results: int):
    """PubMed se PDFs fetch karne ka function."""
    pmcids = []
    page = 1

    for term in search_terms:
        while len(pmcids) < max_results:
            html_content = search_pubmed(term, page)
            if not html_content:
                break
            new_pmcids = extract_pmcids(html_content)
            pmcids.extend(new_pmcids[:max_results])
            page += 1

    return pmcids