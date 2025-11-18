import pymysql

import config

def get_connection():
    """Get a database connection using config values."""
    try:
        conn = pymysql.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASS,
            database=config.DB_NAME
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Connect without specifying DB to create it
        conn = pymysql.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASS
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME}")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Database '{config.DB_NAME}' created or already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")

def create_table():
    """Create the table if it doesn't exist."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {config.DB_CRAWLER_QUEUE_TABLE} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    {config.DB_URL_COLUMN} VARCHAR(255) UNIQUE NOT NULL,
                    {config.DB_PARENT_COLUMN} VARCHAR(255) DEFAULT NULL,
                    depth INT,
                    max_depth INT DEFAULT 0,
                    status ENUM('pending', 'crawled', 'failed') DEFAULT 'pending',
                    insert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    crawled_at TIMESTAMP DEFAULT NULL,
                    failed_at TIMESTAMP DEFAULT NULL
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Table '{config.DB_CRAWLER_QUEUE_TABLE}' created or already exists.")
        except Exception as e:
            print(f"Error creating table: {e}")
            conn.close()

def insert_pending(url, parent, depth, max_depth):
    """Insert a pending URL if not already exists (due to UNIQUE)."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"INSERT IGNORE INTO {config.DB_CRAWLER_QUEUE_TABLE} ({config.DB_URL_COLUMN}, {config.DB_PARENT_COLUMN}, depth, max_depth, status) VALUES (%s, %s, %s, %s, 'pending')", (url, parent, depth, max_depth))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            # The exception here will likely be 'unknown column max_depth' until step 2 is done
            print(f"Error inserting pending {url}: {e}")
            conn.close()

def get_next_pending():
    """Get the next pending URL with the smallest depth and oldest insert."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {config.DB_URL_COLUMN}, {config.DB_PARENT_COLUMN}, depth, max_depth FROM {config.DB_CRAWLER_QUEUE_TABLE} WHERE status='pending' ORDER BY depth ASC, id ASC LIMIT 1")
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row 
        except Exception as e:
            print(f"Error getting next pending: {e}")
            conn.close()
    return None

def mark_crawled(url):
    """Mark a URL as crawled and set crawled_at."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE {config.DB_CRAWLER_QUEUE_TABLE} SET status='crawled', crawled_at=NOW() WHERE {config.DB_URL_COLUMN}=%s", (url,))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error marking {url} as crawled: {e}")
            conn.close()

def mark_failed(url):
    """Mark a URL as failed and set failed_at."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE {config.DB_CRAWLER_QUEUE_TABLE} SET status='failed', failed_at=NOW() WHERE {config.DB_URL_COLUMN}=%s", (url,))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error marking {url} as failed: {e}")
            conn.close()

def get_pending_count():
    """Get count of pending items (queue size)."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {config.DB_CRAWLER_QUEUE_TABLE} WHERE status='pending'")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting pending count: {e}")
            conn.close()
    return 0

def get_crawled_count():
    """Get count of crawled items."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {config.DB_CRAWLER_QUEUE_TABLE} WHERE status='crawled'")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting crawled count: {e}")
            conn.close()
    return 0

def get_failed_count():
    """Get count of failed items."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {config.DB_CRAWLER_QUEUE_TABLE} WHERE status='failed'")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting failed count: {e}")
            conn.close()
    return 0

def clear_table():
    """Clear the table for a new crawl."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"TRUNCATE TABLE {config.DB_CRAWLER_QUEUE_TABLE}")
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Table '{config.DB_CRAWLER_QUEUE_TABLE}' cleared.")
        except Exception as e:
            print(f"Error clearing table: {e}")
            conn.close()