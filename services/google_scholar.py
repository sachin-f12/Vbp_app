import os
from utils.search_utils import search_google_scholar, extract_pdf_links
import asyncio


async def fetch_google_scholar_results(search_terms: list[str], max_results: int):
    print('7777777777777')
    """Fetches Google Scholar PDF links asynchronously."""
    pdf_links = set()  # Use a set to avoid duplicates
    start = 0

    for term in search_terms:
        while len(pdf_links) < max_results+5:
            data = await asyncio.to_thread(search_google_scholar, term, start)  # Run sync function in thread
            if not data:
                break  # Stop if we get no data
            
            new_links = set(extract_pdf_links(data))  # Convert to set to avoid adding duplicates

            pdf_links.update(new_links)

            # Stop when we reach max_results
            if len(pdf_links) >= max_results:
                break  

            start += 10
            await asyncio.sleep(1)  # Delay to avoid rate limiting

    return list(pdf_links)[:max_results]  # Convert set back to list