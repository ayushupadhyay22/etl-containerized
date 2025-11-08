import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
import os
import time

# --- Configuration from Environment Variables ---
WEBSITE_URL = os.getenv('WEBSITE_URL', 'http://quotes.toscrape.com/')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'mydatabase')
DB_USER = os.getenv('DB_USER', 'myuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'mypassword')
DB_PORT = int(os.getenv('DB_PORT', 5432))

def wait_for_db():
    """Waits for the PostgreSQL database to be ready."""
    print("Waiting for PostgreSQL to be ready...")
    retries = 10
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT,
                connect_timeout=5
            )
            conn.close()
            print("PostgreSQL is ready!")
            return True
        except psycopg2.OperationalError as e:
            print(f"PostgreSQL not ready yet: {e}. Retrying in 5 seconds...")
            time.sleep(5)
            retries -= 1
    print("Failed to connect to PostgreSQL after multiple retries.")
    return False

def create_table_if_not_exists():
    """Connects to PostgreSQL and creates the table if it doesn't exist."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS website_data (
                id SERIAL PRIMARY KEY,
                title TEXT,
                url TEXT,
                content TEXT,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("Table 'website_data' ensured to exist.")
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

def fetch_data_from_website(url):
    """Fetches HTML content from a given URL."""
    print(f"Fetching data from {url}...")
    try:
        response = requests.get(url, timeout=10) # Add a timeout
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def parse_website_data(html_content):
    """Parses HTML content to extract relevant data."""
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_records = []

    # Example: Extracting quotes and authors from quotes.toscrape.com
    quotes = soup.find_all('div', class_='quote')
    if not quotes:
        print("No quotes found on the page. Check website structure or URL.")
        return []

    for quote in quotes:
        try:
            text = quote.find('span', class_='text').get_text(strip=True)
            author = quote.find('small', class_='author').get_text(strip=True)
            extracted_records.append({
                'title': author,
                'url': WEBSITE_URL, # Or the specific URL of the page the data came from
                'content': text
            })
        except AttributeError as e:
            print(f"Skipping a quote due to missing element: {e}")
            continue
    return extracted_records

def save_to_postgres(records):
    """Connects to PostgreSQL and saves the processed records."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cur = conn.cursor()

        for record in records:
            cur.execute(
                "INSERT INTO website_data (title, url, content, extracted_at) VALUES (%s, %s, %s, %s)",
                (record['title'], record['url'], record['content'], datetime.now())
            )
        conn.commit()
        print(f"Successfully inserted {len(records)} records into PostgreSQL.")

    except psycopg2.Error as e:
        print(f"Error connecting to or interacting with PostgreSQL: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    if not wait_for_db():
        exit(1) # Exit if DB is not ready

    create_table_if_not_exists()

    html = fetch_data_from_website(WEBSITE_URL)

    if html:
        print("Parsing data...")
        processed_data = parse_website_data(html)

        if processed_data:
            print("Saving data to PostgreSQL...")
            save_to_postgres(processed_data)
        else:
            print("No data extracted from the website.")
    else:
        print("Failed to fetch website content.")
