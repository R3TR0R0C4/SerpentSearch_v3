## Project Architecture
The project is organized into several files for separation of concerns:

* config.py: Holds configuration variables like database credentials
    * (DB_HOST, DB_USER, DB_PASS, DB_NAME)
    * table/column names (e.g., DB_CRAWLER_TABLE = 'urls', DB_URL_COLUMN = 'url')
    * file paths (OUTPUT_PATH = 'crawled_urls.txt'), and defaults (MAX_DEPTH_DEFAULT = 2)

* models.py: Handles all database operations using pymysql. Key functions:
    * get_connection(): Establishes a MariaDB connection.
    * create_database() and create_table(): Set up the DB and table (run once for initialization).
    * insert_pending(url, parent, depth): Adds a URL as 'pending' (uses INSERT IGNORE for uniqueness).
    * get_next_pending(): Fetches the next 'pending' URL (ordered by depth ASC, then ID ASC).
    * mark_crawled(url): Updates status to 'crawled' and sets crawled_at timestamp.
    * get_pending_count() and get_crawled_count(): Count rows by status for stats.
    * clear_table(): Truncates the table for new crawls.

    The table schema (in create_table()):
    * id: AUTO_INCREMENT PRIMARY KEY
    * url: VARCHAR(255) UNIQUE NOT NULL
    * parent_url: VARCHAR(255) DEFAULT NULL
    * depth: INT
    * status: ENUM('pending', 'crawled') DEFAULT 'pending'
    * insert_time: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    * crawled_at: TIMESTAMP DEFAULT NULL

* crawler.py: Core crawling logic.
    * fetch_page(url): GETs the page content with requests (adds User-Agent header for better compatibility).
    * extract_links(content, base_url): Parses HTML with BeautifulSoup to get absolute links.
    * store_data(url, parent): Appends to TXT file (backup; DB storage is handled in models.py).
    * crawl(start_url, max_depth, output_path): Main loop using DB as queue:
        1. Insert start_url as pending (depth 0, no parent).
        2. While pending items exist:
            * Get next pending (url, parent, depth).
            * If depth > max_depth or fetch fails, skip.
            * Fetch content, mark as crawled, store to file.
            * If depth < max_depth, extract links and insert as pending children.


* app.py: Flask web application.
  * Routes:
        * /: Temporarily redirects /admin, when search capability is added it will be the search page.
        * /admin (GET): Renders admin.html with form for start_url and max_depth.
        * /admin/crawl (POST): Clears table, starts crawl in background thread, shows message.
        * /admin/stats (GET): Returns JSON {'pending': count, 'crawled': count}.

    * Uses threading for non-blocking crawls.

* run.py: CLI entry point (optional, for non-web use).
    * Parses args: python run.py <start_url> [max_depth].
    * Calls crawl() directly.

* templates/admin.html: HTML form for inputs, displays message, and stats (queue size, crawled items). Notes "Statistics refresh every 5 seconds."
* static/js/app.js: JavaScript for polling /admin/stats every 5s via fetch(), updating DOM elements (#queue-size, #crawled-items).

## Setup Process

1. Install Dependencies:
    * Python libraries: pip install requests beautifulsoup4 pymysql flask.
    * MariaDB: Install server, create root user if needed.

2. Configure config.py:
    * Update DB credentials and names.
    * Ensure MariaDB is running.

Folder Structure:

```textproject/
├── app.py
├── config.py
├── crawler.py
├── models.py
├── run.py
├── templates/
│   └── admin.html
└── static/
    └── js/
        └── app.js
```

## Crawling Process
The crawler uses a database-backed queue for persistence and state management:

1. Start Crawl:
    * Via web: Submit form on /admin → POST to /admin/crawl → Clear table → Thread starts crawl().
    * Via CLI: python run.py <url> [depth] → Calls crawl().

2. Initialization:
    * Insert start_url as 'pending' (depth 0, parent None).

3. Main Loop (in crawl()):
    * While pending items:
        * Fetch next pending (lowest depth, oldest).
        * Skip if depth > max_depth or fetch fails.
        * Fetch page content.
        * Mark as 'crawled' (update status and timestamp).
        * Store to TXT (url | parent).
        * If depth < max_depth: Extract links, insert unique children as 'pending'.

4. Status Meanings:
    * Pending: URL discovered but not yet fetched/processed (to-do queue).
    * Crawled: URL successfully fetched, links extracted (if applicable), marked done.
    * No content storage or indexing—just URL metadata for now.

5. Error Handling:
    * Fetch errors: Skip, leave pending (could add retries).
    * DB errors: Printed to console.


## Monitoring Process (Web App)

1. Start a Crawl: Form submission triggers background thread—no page block.
2. Real-Time Stats:
    * JS polls /admin/stats every 5s.
    * Endpoint queries DB counts (pending = queue size, crawled = completed).
    * Updates displayed on page.
3. User Feedback: Message after submit (e.g., "Crawl started... Monitor statistics below.").

## How to Run

* Web Mode: python app.py → Visit http://127.0.0.1:5000/admin.
* CLI Mode: python run.py https://example.com 2. (very basic usage)
* Test with small depth to avoid long runs or anti-scraping blocks (e.g., Reddit may throttle).
