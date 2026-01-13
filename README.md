> [!CAUTION]
> This was a project to practice and fulfill some curiosity of mine, it's not maintained, and probably not meant for anything.


# SerpentSearch v3

A simple Python web crawler that finds and saves URLs.

## Overview

SerpentSearch v3 is a straightforward web crawler. You give it a starting website, and it digs for links, saving everything it finds in a MariaDB database.

It works by checking all links on the starting page (level 1) before moving on to the links *on those pages* (level 2), and so on. You can tell it exactly how deep to go so it doesn't crawl the whole internet.

-----

## Features

  * **Digs for links**: Crawls websites up to a depth you set.
  * **Finds all links**: Scans the HTML of a page to find new URLs.
  * **Saves what it finds**: Stores all discovered URLs in a MariaDB database so you can look at them later.
  * **Handles errors**: Deals with network problems or bad HTML without crashing.
  * **Easy to tweak**: All settings are in a single `config.py` file.

-----

## Requirements

  * Python 3.x
  * A MariaDB or MySQL server
  * A few Python packages:
      * `requests` (to get web pages)
      * `beautifulsoup4` (to parse the HTML)
      * `pymysql` (to talk to the database)
      * `Flask` (to serve the webpage)

-----

## Installation

1.  **Install the Python libraries:**

    ```bash
    pip install requests beautifulsoup4 pymysql Flask
    ```

2.  **Set up your database**: Make sure your MariaDB server is running.

3.  **Update the config**: Edit `config.py` and put in your database username, password, etc.

-----

## Configuration

You can change all the main settings in `config.py`:

  * **DB_HOST**: Your database server (default: `localhost`)
  * **DB_USER**: Your database username (default: `serpentsearch`)
  * **DB_PASS**: Your database password (default: `serpentsearch`)
  * **DB_NAME**: The name of the database (default: `serpentsearch_v3`)
  * **DB_CRAWLER_QUEUE_TABLE**: The table where URLs are stored (default: `crawl_queue`)
  * **MAX_DEPTH_DEFAULT**: The default crawl depth (default: `2`)

-----

## Architecture

We've got a separate document explaining how it's all put together: [Architecture](https://www.google.com/search?q=./docs/architecture.md)

-----

## Notes

  * Heads up: This is still a **work-in-progress (WIP)**.
  * It saves a timestamp for every URL it crawls.
  * The crawler will stop when it hits the `max_depth` you set.
  * It keeps track of duplicates so it doesn't crawl the same page more than once.

-----

## What's Next (To-Do List)

  * Respect `robots.txt` files and add crawl delays (to be a good bot).
  * Add filters to only crawl certain types of URLs.
  * Make the "don't crawl duplicates" check more efficient.
  * Show stats and progress while the crawl is running.
  * Start a indexer
  * Start a search page with [Whoosh](https://github.com/whoosh-community/whoosh) 
