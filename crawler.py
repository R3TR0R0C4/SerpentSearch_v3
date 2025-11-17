import requests
from bs4 import BeautifulSoup
import urllib.parse

import models

def fetch_page(url):
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
    links = []
    try:
        soup = BeautifulSoup(content, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            abs_url = urllib.parse.urljoin(base_url, href)
            if abs_url.startswith('http') or abs_url.startswith('https'):
                links.append(abs_url)
    except Exception as e:
        print(f"Error extracting links from {base_url}: {e}")
    return links

def crawl(start_url, max_depth):
    models.insert_pending(start_url, None, 0)
    
    while True:
        pending = models.get_next_pending()
        if not pending:
            break
        
        current_url, current_parent, current_depth = pending
        
        if current_depth > max_depth:
            continue  # Skip, leave as pending or delete if needed
        
        content = fetch_page(current_url)
        if not content:
            continue  # Skip if fetch fails
        
        models.mark_crawled(current_url)
        print(f"Visiting {current_url} at depth {current_depth}")
        
        models.mark_crawled(current_url)
        
        if current_depth < max_depth:
            links = extract_links(content, current_url)
            for link in links:
                models.insert_pending(link, current_url, current_depth + 1)
