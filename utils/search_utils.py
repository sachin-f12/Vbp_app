import os
import requests

def search_google_scholar(keyword, start=0):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_scholar",
        "q": keyword,
        "api_key": os.getenv("SERP_API_KEY"),
        "start": start
    }
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        print(f"Error in search_google_scholar: {e}")
        return None

def extract_pdf_links(data):
    links = []
    for result in data.get("organic_results", []):
        for resource in result.get("resources", []):
            if resource.get("file_format") == "PDF":
                links.append(resource["link"])
    return links
