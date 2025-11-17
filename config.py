# Database configuration (for MariaDB)
DB_HOST = 'localhost'
DB_USER = 'serpentsearch'
DB_PASS = 'serpentsearch'
DB_NAME = 'serpentsearch_v3'
DB_TABLE = 'crawl_queue'

# Database column table names
DB_URL_COLUMN = 'url'  # Column name for the URL
DB_PARENT_COLUMN = 'parent_url'  # Column name for the parent URL

# Other crawl settings
MAX_DEPTH_DEFAULT = 2  # Crawler depth
