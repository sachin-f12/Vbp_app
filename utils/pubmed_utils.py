# pubmed_utils.py
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

def download_pdf(pmcid, dir):
    """
    Download PDF with improved error handling and URL construction
    """
    session = create_session()
    Path(dir).mkdir(parents=True, exist_ok=True)
    pdf_path = Path(dir) / f"{pmcid}.pdf"
    
    # Skip if already downloaded
    if pdf_path.exists() and pdf_path.stat().st_size > 1000:
        logging.info(f"PDF already exists for {pmcid}")
        return True
    
    try:
        pdf_url = get_pdf_link(session, pmcid)
        if not pdf_url:
            logging.error(f"Could not find PDF link for {pmcid}")
            return False
        
        for attempt in range(RETRIES):
            try:
                # Add required headers for PDF download
                headers = {
                    'User-Agent': USER_AGENT,
                    'Accept': 'application/pdf',
                    'Referer': f"{BASE_URL}{pmcid}/"
                }
                
                response = session.get(pdf_url, headers=headers, stream=True, timeout=30)
                response.raise_for_status()
                
                # Verify content type
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and 'octet-stream' not in content_type:
                    logging.error(f"Invalid content type for {pmcid}: {content_type}")
                    return False
                
                # Download PDF
                with open(pdf_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                
                # Verify file size
                if pdf_path.stat().st_size < 1000:
                    pdf_path.unlink()
                    logging.error(f"Downloaded file too small for {pmcid}")
                    return False
                
                logging.info(f"Successfully downloaded PDF for {pmcid}")
                return True
                
            except requests.exceptions.RequestException as e:
                if attempt + 1 == RETRIES:
                    raise
                time.sleep(BACKOFF_FACTOR * (2 ** attempt))
                
    except Exception as e:
        logging.error(f"Failed to download PDF for {pmcid}: {e}")
        if pdf_path.exists():
            pdf_path.unlink()
        return False
    finally:
        session.close()