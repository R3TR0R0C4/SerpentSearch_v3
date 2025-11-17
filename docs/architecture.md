## Project Architecture

We split the project into several files to keep things organized. Each file has a specific job:

  * **`config.py`**: This is where we keep all the settings. Think database logins (`DB_HOST`, `DB_USER`, etc.), names for our tables and columns, and default values like the `MAX_DEPTH_DEFAULT`.

  * **`models.py`**: This file talks to the MariaDB database (using `pymysql`). It's responsible for:

      * Connecting to the DB (`get_connection`).
      * Setting up the database and table the first time (`create_database`, `create_table`).
      * Adding new URLs to the queue (`insert_pending`). We use `INSERT IGNORE` so we don't add duplicates.
      * Grabbing the next URL to crawl (`get_next_pending`). It prioritizes by depth first, then by the oldest entry.
      * Updating a URL's status to 'crawled' (`mark_crawled`).
      * Getting stats for the web UI (`get_pending_count`, `get_crawled_count`).
      * Wiping the table for a fresh start (`clear_table`).

    The database table itself is pretty straightforward: `id`, `url` (which must be unique), `parent_url`, `depth`, `status` ('pending' or 'crawled'), and timestamps.

  * **`crawler.py`**: This is the heart of the crawler.

      * `fetch_page(url)`: Grabs the HTML from a URL. It sends a `User-Agent` header to look more like a real browser.
      * `extract_links(content, base_url)`: Uses BeautifulSoup to find all the links on the page and make sure they're absolute (e.g., `/about` becomes `http://example.com/about`).
      * `store_data(url, parent)`: A simple backup that just appends the crawled URL to a text file.
      * `crawl(start_url, max_depth)`: This is the main function. It uses the database as its to-do list:
        1.  Adds the `start_url` to the queue.
        2.  Keeps looping as long as there are 'pending' URLs.
        3.  It grabs the next URL, fetches it, marks it 'crawled', and saves it to the text file.
        4.  If the crawler isn't too deep (the depth of the link isn't bigger than the configured depth), it finds all the links on that page and adds them to the queue as 'pending'.

  * **`app.py`**: This is the Flask web app that provides a simple UI.

      * `/`: Just forwards you to the admin page for now.
      * `/admin` (GET): Shows the admin page with the form to start a crawl.
      * `/admin/crawl` (POST): This is what the form submits to. It clears the database and then starts the crawling process in a background thread. This is important so the web page doesn't freeze while the crawl is running.
      * `/admin/stats` (GET): A JSON endpoint for the frontend to get live stats (how many URLs are pending vs. crawled).

  * **`run.py`**: A simple script if you just want to run the crawler from your terminal without the web UI. (may be removed in the future)

  * **`templates/admin.html`**: The HTML for the `/admin` page. It has the form and the stats.

  * **`static/js/app.js`**: A bit of JavaScript that calls the `/admin/stats` endpoint every 5 seconds and updates the "Queue Size" and "Items Crawled" numbers on the page.

-----

## Getting Started

1.  **Dependencies**: You'll need the Python libraries (`pip install requests beautifulsoup4 pymysql flask`) and a MariaDB server.
2.  **Edit `config.py`**: Open `config.py` and put in your MariaDB username, password, and database name. Make sure your MariaDB server is running\!

### Folder Structure

```text
project/
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

-----

## How the Crawl Works

The main idea is using the database as a persistent to-do list (queue). This helps manage the state and means we don't lose progress if the script stops.

1.  **How to start**: You can either hit the "Start Crawl" button on the web UI (`/admin`) or run `python3 run.py <url> <depth>` from the command line.

2.  **The Loop**:

      * First, the `start_url` is added to the database as 'pending' at depth 0.
      * The crawler keeps grabbing the next 'pending' URL (it picks the one with the lowest depth first).
      * It **skips** the URL if it's deeper than the `max_depth` or if the page fails to load.
      * Otherwise, it fetches the page, marks the URL as 'crawled' in the DB, and saves the URL to the backup text file.
      * If it's not at the max depth, it scans the page for new links and adds them to the DB as 'pending'.

3.  **Status Meanings**:

      * **Pending**: It's in the queue to be crawled.
      * **Crawled**: It's done.

4.  **Error Handling**: Right now, if a page fails to fetch, it's just skipped and left as 'pending'. Database errors will just print to the console.

-----

## How to Run It

  * **Web App**: Run `python3 app.py` and open `http://127.0.0.1:5000/admin` in your browser.
  * **Command Line**: Run `python3 run.py https://example.com 2`.

**A quick tip**: Start with a small depth (like 1 or 2). If you try to crawl a huge site, you might get throttled or blocked.