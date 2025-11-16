import pymysql
import config  # Import your config for DB details

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
                CREATE TABLE IF NOT EXISTS {config.DB_CRAWLER_TABLE} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    {config.DB_URL_COLUMN} VARCHAR(255) NOT NULL,
                    {config.DB_PARENT_COLUMN} VARCHAR(255) DEFAULT NULL,
                    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Table '{config.DB_CRAWLER_TABLE}' created or already exists.")
        except Exception as e:
            print(f"Error creating table: {e}")
            conn.close()

def insert_url(url, parent):
    """Insert a URL and its parent into the table."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {config.DB_CRAWLER_TABLE} (url, parent_url) VALUES (%s, %s)", (url, parent))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Stored {url} (parent: {parent}) in MariaDB")
        except Exception as e:
            print(f"Error storing {url} in MariaDB: {e}")
            conn.close()