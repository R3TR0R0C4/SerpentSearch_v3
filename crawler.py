import os
import requests
import random
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

import models
import control


def get_url_status(url: str) -> str:
    """
    Determine how a URL should be classified based on its file extension.

    Returns:
        'media'       → Images, videos, audio, documents, archives  
        'web-support' → Scripts, stylesheets, fonts, manifests  
        'pending'     → Everything else (likely HTML pages)  
    """
    parsed = urlparse(url)
    _, ext = os.path.splitext(parsed.path.lower())

    # Media file extensions (treated as "non-crawlable" but counted separately)
    if ext in {
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico', '.tiff', '.tif',
        '.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.flv', '.wmv',
        '.mp3', '.wav', '.flac', '.aac',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.rar', '.7z', '.tar', '.gz'
    }:
        return 'media'

    # Auxiliary web resources (scripts, styles, fonts)
    if ext in {
        '.js', '.mjs', '.css', '.scss', '.sass',
        '.woff', '.woff2', '.ttf', '.otf', '.eot',
        '.json', '.xml', '.webmanifest', '.map'
    }:
        return 'web-support'

    # Default: treat as a normal page to crawl
    return 'pending'


def fetch_page(url):
    """
    Download a webpage using randomized headers and a small artificial delay
    to mimic human browsing behavior.

    Returns:
        str (HTML content) or None if request failed.
    """
    # Randomize user-agent to avoid bot detection
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    ]

    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    # Add random delay to reduce bot-like patterns
    time.sleep(random.uniform(0.5, 2))

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}: Status code {response.status_code}")
            return None

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def fetch_page_old(url):
    """
    Legacy/simple version of fetch_page() kept for comparison or fallback.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}: Status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_links(content, base_url):
    """
    Parse HTML and extract all <a href="..."> links.

    Args:
        content: HTML content of a page.
        base_url: URL used for resolving relative links.

    Returns:
        A list of absolute URLs.
    """
    links = []
    try:
        soup = BeautifulSoup(content, 'html.parser')

        # Extract all anchor tags with href attribute
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # Convert relative links to absolute URLs
            abs_url = urljoin(base_url, href)

            # Only keep valid HTTP/HTTPS URLs
            if abs_url.startswith('http'):
                links.append(abs_url)

    except Exception as e:
        print(f"Error extracting links from {base_url}: {e}")

    return links


def crawl():
    """
    Main crawler loop.

    Continues processing pending URLs from the database until exhausted.
    Respects pause state.
    """
    while True:

        # Read pause state under lock to prevent race conditions
        with control.lock:
            is_paused_status = control.is_paused

        # If paused, temporarily sleep and skip processing
        if is_paused_status:
            time.sleep(0.5)
            continue

        # Fetch next pending URL from storage
        pending = models.get_next_pending()

        # No more URLs → stop crawling
        if not pending:
            break

        current_url, current_parent, current_depth, max_depth = pending

        # Fetch the page contents
        content = fetch_page(current_url)

        # Fetch failure → mark it and continue
        if not content:
            models.mark_failed(current_url)
            continue

        # Mark as successfully crawled
        models.mark_crawled(current_url)
        print(f"Visiting {current_url} at depth {current_depth}")

        # If depth limit not reached → extract and enqueue new links
        if current_depth < max_depth:
            links = extract_links(content, current_url)

            for link in links:
                # Determine if link is media, script, page, etc.
                link_status = get_url_status(link)

                # Add new item to the pending queue
                models.insert_pending(
                    link,
                    current_url,
                    current_depth + 1,
                    max_depth,
                    status=link_status
                )
