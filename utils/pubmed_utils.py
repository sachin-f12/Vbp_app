import requests
from bs4 import BeautifulSoup
import logging
from pathlib import Path
import time
import re
PUBMED_SEARCH_URL = "https://www.ncbi.nlm.nih.gov/pmc/?term="
BASE_URL = 'https://www.ncbi.nlm.nih.gov/pmc/articles/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
CHUNK_SIZE = 1024
RETRIES = 3
BACKOFF_FACTOR = 0.3

OUTPUT_DIR = Path("download/PubMed")
# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    })
    return session

def search_pubmed(term, page=1, retries=RETRIES, backoff_factor=BACKOFF_FACTOR):
    url = f"{PUBMED_SEARCH_URL}{term.replace(' ', '+')}&page={page}"
    session = create_session()
    
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            logging.info(f"Successfully fetched search results for term: {term}, page: {page}")
            return response.text
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt + 1 == retries:
                logging.error("Max retries exceeded")
                raise
            time.sleep(backoff_factor * (2 ** attempt))
    return None

def extract_pmcids(html_content):
    if not html_content:
        print("HTML content is empty.")
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    pmcids = []
    
    # Find articles in the search results
    articles = soup.find_all('div', class_='rslt')
    print(f"Number of articles found: {len(articles)}")
    
    for article in articles:
        print("Article HTML:", article)
        
        # Look for links in the article
        links = article.find_all('a', href=True)
        print(f"Links in article: {len(links)}")
        
        for link in links:
            href = link['href']
            print(f"Link href: {href}")
            
            # Match the pattern for PMC IDs
            if '/articles/PMC' in href:
                pmcid_match = re.search(r'PMC(\d+)', href)
                if pmcid_match:
                    pmcid_str = f"PMC{pmcid_match.group(1)}"
                    print(f"Extracted PMC ID: {pmcid_str}")
                    if pmcid_str not in pmcids:  # Avoid duplicates
                        pmcids.append(pmcid_str)
    
    print(f"Total extracted PMCIDs: {len(pmcids)}")
    return pmcids


def get_pdf_link(session, pmcid):
    """
    Get the correct PDF download link using multiple methods
    """
    article_url = f"{BASE_URL}{pmcid}/"
    try:
        response = session.get(article_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Method 1: Find PDF link in download section
        download_section = soup.find('div', class_='format-menu')
        if download_section:
            pdf_link = download_section.find('a', {'href': re.compile(r'.*\.pdf$')})
            if pdf_link and pdf_link.get('href'):
                return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
        
        # Method 2: Look for direct PDF download button
        pdf_buttons = soup.find_all('a', string=re.compile(r'PDF|Download PDF'))
        for button in pdf_buttons:
            href = button.get('href', '')
            if href.endswith('.pdf') or '/pdf/' in href:
                return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
        
        # Method 3: Check for alternative PDF format links
        links = soup.find_all('a', href=re.compile(r'.*\.pdf$|/pdf/'))
        for link in links:
            href = link.get('href', '')
            if href:
                if href.startswith('http'):
                    return href
                else:
                    return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
        
        logging.error(f"No PDF link found for {pmcid}")
        return None
        
    except Exception as e:
        logging.error(f"Error getting PDF link for {pmcid}: {e}")
        return None



def sanitize_filename(filename):
    """Sanitize folder names to remove invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_pdf(pmcid, search_term, search_source="PubMed"):
    """Download the PDF and store it in a dynamically created search-term-based directory."""
    
    # Sanitize the search term to create a valid folder name
    safe_search_term = sanitize_filename(search_term)

    # Determine correct storage directory
    if search_source == "BOTH":
        output_dir = Path(f"download/Both/PubMed/{safe_search_term}")
    else:
        output_dir = Path(f"download/PubMed/{safe_search_term}")

    output_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    pdf_path = output_dir / f"{pmcid}.pdf"

    # Skip if already downloaded
    if pdf_path.exists() and pdf_path.stat().st_size > 1000:
        logging.info(f"PDF already exists: {pdf_path}")
        return str(pdf_path)

    # Download process remains the same
    session = create_session()
    try:
        pdf_url = get_pdf_link(session, pmcid)
        if not pdf_url:
            logging.error(f"Could not find PDF link for {pmcid}")
            return None

        headers = {'User-Agent': USER_AGENT, 'Accept': 'application/pdf'}
        response = session.get(pdf_url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        with open(pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

        if pdf_path.stat().st_size < 1000:
            pdf_path.unlink()
            logging.error(f"Downloaded file too small for {pmcid}")
            return None

        logging.info(f"Successfully downloaded PDF: {pdf_path}")
        return str(pdf_path)

    except Exception as e:
        logging.error(f"Failed to download PDF for {pmcid}: {e}")
        return None
    finally:
        session.close()