from crawler import crawl
import models
import config

import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run.py <start ulr> [max crawl depth]")
        print("Example. pytohn3 run.py https://reddit.com 4")

    start_url = sys.argv[1]
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else sys.config.MAX_DEPTH_DEFAULT

    #Create db and tables if non existant
    models.create_database()
    models.create_table()

    print(f"Starting crawl from {start_url} with max depth {max_depth}")
    crawl(start_url, max_depth)

if __name__ == "__main__":
    main()