# SerpentSearch v3

A web crawler built in Python that recursively discovers and stores URLs from a starting point.

## Overview

SerpentSearch v3 is a simple web crawler designed to traverse websites, extract links, and store discovered URLs in a MariaDB database. It uses a breadth-first search approach with configurable depth limits to control crawling scope.

## Features

- **Recursive Web Crawling**: Traverses websites up to a specified depth
- **Link Extraction**: Parses HTML to find and extract all links from pages
- **Database Storage**: Stores crawled URLs in MariaDB for later analysis
- **Error Handling**: Gracefully handles network errors and parsing failures
- **Configurable Settings**: Easy-to-modify configuration for different crawl parameters

## Requirements

- Python 3.x
- MariaDB/MySQL server
- Python packages:
  - `requests` - HTTP requests
  - `beautifulsoup4` - HTML parsing
  - `pymysql` - MariaDB/MySQL connector

## Installation

1. Install dependencies:
```bash
pip install requests beautifulsoup4 pymysql
```

2. Set up MariaDB database and create the required table (use `creates.sql`)

3. Update `config.py` with your database credentials

## Configuration

Edit `config.py` to customize:

- **DB_HOST**: Database server hostname (default: `localhost`)
- **DB_USER**: Database username (default: `serpentsearch`)
- **DB_PASS**: Database password (default: `serpentsearch`)
- **DB_NAME**: Database name (default: `serpentsearch_v3`)
- **DB_CRAWLER_TABLE**: Table name for storing URLs (default: `crawl_queue`)
- **MAX_DEPTH_DEFAULT**: Maximum crawl depth (default: `2`)

## Usage

Run the crawler from the command line:

```bash
python crawler.py
```

This will start crawling from `https://www.reddit.com/` with a maximum depth of 2.

To customize the start URL and depth, modify the last line in `crawler.py`:

```python
crawl("https://example.com/", max_depth)
```

## Database Schema

The crawler stores data in the `crawl_queue` table:

```sql
CREATE TABLE IF NOT EXISTS serpentsearch_v3.crawl_queue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(255) NOT NULL,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## How It Works

1. **Fetch Page**: Downloads HTML content from a URL
2. **Extract Links**: Parses HTML and extracts all hyperlinks
3. **Store Data**: Saves the URL to the database
4. **Queue Processing**: Adds newly discovered links to a processing queue
5. **Depth Control**: Respects the maximum depth limit to prevent infinite crawling

## Project Structure

```
.
├── crawler.py         # Main crawler implementation
├── config.py          # Configuration settings
├── creates.sql        # Database schema
└── README.md          # This file
```

## Notes

- This is a work-in-progress (WIP) project
- URLs are stored with a timestamp of when they were crawled
- The crawler respects the `max_depth` parameter to limit crawl scope
- Duplicate URLs are tracked to avoid re-crawling the same page

## Future Enhancements

- Respect `robots.txt` and crawl delays
- Add filtering for specific URL patterns
- Implement URL deduplication more efficiently
- Add progress tracking and statistics
- Support for different parsing strategies
