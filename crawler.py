import urllib.parse
import requests
import random
import time

from bs4 import BeautifulSoup

import models
import config
import control


def fetch_page(url):
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
    time.sleep(random.uniform(1, 3))  # Random delay to mimic human behavior
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


def crawl():    
    while True:
        with control.lock:
            is_paused_status = control.is_paused

        if is_paused_status:
            time.sleep(0.5)
            continue

        pending = models.get_next_pending()
        if not pending:
            break
        
        current_url, current_parent, current_depth, max_depth = pending
        
        content = fetch_page(current_url)
        if not content:
            models.mark_failed(current_url)
            continue
        

        models.mark_crawled(current_url)
        print(f"Visiting {current_url} at depth {current_depth}")
                
        if current_depth < max_depth:
            links = extract_links(content, current_url)
            for link in links:
                models.insert_pending(link, current_url, current_depth + 1, max_depth)