import requests
from bs4 import BeautifulSoup
import urllib.parse
from collections import deque
import pymysql

import config
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

def store_data(url, db_host='localhost', db_user='serpentsearch', db_pass='serpentsearch', db_name='serpentsearch_v3'):
    try:
        conn = pymysql.connect(host=db_host, user=db_user, password=db_pass, database=db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO crawl_queue (url) VALUES (%s)", (url,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Stored {url} in MariaDB")
    except Exception as e:
        print(f"Error storing {url} in MariaDB: {e}")

def store_data_old(url):
    try:
        conn = pymysql.connect(host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASS, database=config.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {config.DB_CRAWLER_TABLE} (url) VALUES (%s)", (url,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Stored {url} in MariaDB")
    except Exception as e:
        print(f"Error storing {url} in MariaDB: {e}")

def crawl(start_url, max_depth):
    queue = deque([(start_url, None, 0)])
    visited = set()
    
    while queue:
        current_url, current_parent, current_depth = queue.popleft()
        
        if current_url in visited or current_depth > max_depth:
            continue
        
        visited.add(current_url)
        print(f"Visiting {current_url} at depth {current_depth}")
        
        models.insert_url(current_url, current_parent)
        
        if current_depth < max_depth:
            content = fetch_page(current_url)
            if content:
                links = extract_links(content, current_url)
                for link in links:
                    if link not in visited:
                        queue.append((link, current_url, current_depth + 1))