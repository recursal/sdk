import requests
import csv
import sqlite3
import os

from bs4 import BeautifulSoup

TEMPLATE_FILE=os.path.join(os.path.dirname(__file__), 'test-cases.base.csv')
DB_PATH=os.path.join(os.path.dirname(__file__), 'moderation.db')

def get_db_connection():
  return sqlite3.connect(DB_PATH)

# Function to create a SQLite database and table
def ensure_table(conn):
  c = conn.cursor()
  c.execute('''CREATE TABLE IF NOT EXISTS memoization (
    url TEXT PRIMARY KEY,
    annotation TEXT,
    label TEXT,
    html TEXT
  )''')
  conn.commit()

def get_meta_description(page_content):
  soup = BeautifulSoup(page_content, features='html.parser')
  t = soup.find('meta', {'name': 'description'})
  return t.get('content') if t else None

def init_db():
  with open(TEMPLATE_FILE, 'r') as csvfile, get_db_connection() as conn:
    ensure_table(conn)
    spamreader = csv.DictReader(csvfile)
    c = conn.cursor()

    for row in spamreader:
      try:
        url = row['URL']
        annotation = row['Annotation']
        label = row['Label']
        print(f"Processing {url} ...")

        c.execute("SELECT html FROM memoization WHERE url=?", (url,))
        result = c.fetchone()
        if result:
          print("Already memoized")
          continue

        # ok, URL isn't memoized. do it.
        html = requests.get(url).text
        c.execute("INSERT INTO memoization (url, annotation, label, html) VALUES (?, ?, ?, ?)", (url, annotation, label, html))
        conn.commit()

      except Exception as e:
        print(f"Failure with {url}: {e}. Skipping.")
        pass

if __name__ == "__main__":
  init_db()

