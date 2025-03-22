import os
from utils.search_utils import search_google_scholar, extract_pdf_links
from utils.download_utils import download_pdf_using_selenium


# async def fetch_google_scholar_results(search_terms: list[str], max_results: int):
#     """Google Scholar se PDFs fetch karne ka function."""
#     pdf_links = []
#     start = 0
#     max_retries = 3  # Agar 3 baar data nahi mila toh loop break

#     for term in search_terms:
#         retries = 0
#         while len(pdf_links) < max_results:
#             print(f"Searching Google Scholar for: {term}, Start: {start}")
#             data = search_google_scholar(term, start)

#             if not data:
#                 retries += 1
#                 if retries >= max_retries:
#                     print(f"❌ Max retries reached for {term}. Stopping search.")
#                     break
#                 print(f"🔄 Retrying... ({retries}/{max_retries})")
#                 continue

#             new_links = extract_pdf_links(data)
#             pdf_links.extend(new_links)
#             pdf_links = pdf_links[:max_results]
#             start += 10

#     print(f"Google Scholar Results: {pdf_links}")
#     return pdf_links

async def fetch_google_scholar_results(search_terms: list[str], max_results: int):
    """Google Scholar se PDFs fetch karne ka function."""
    pdf_links = []
    start = 0

    for term in search_terms:
        while len(pdf_links) < max_results:
            data = search_google_scholar(term, start)
            if not data:
                break
            new_links = extract_pdf_links(data)
            pdf_links.extend(new_links)
            pdf_links = pdf_links[:max_results]
            start += 10

    return pdf_links
