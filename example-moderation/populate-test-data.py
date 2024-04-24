import requests
import csv
from bs4 import BeautifulSoup
import os

# disable ssl verification for requests ...
os.environ['REQUESTS_CA_BUNDLE'] = ""
os.environ['CURL_CA_BUNDLE'] = ""

def get_meta_description(page_content):
  soup = BeautifulSoup(page_content, features='html.parser')
  t = soup.find('meta', {'name': 'description'})
  return t.get('content') if t else None

TEMPLATE_FILE='examples.base.csv'
OUT_FILE='examples.csv'

with open(OUT_FILE, 'w') as outfile:
  out = csv.DictWriter(outfile, ["URL", "Annotation", "Label", "meta_description"])
  out.writeheader()

  with open(TEMPLATE_FILE, 'r') as csvfile:
    spamreader = csv.DictReader(csvfile)

    for row in spamreader:
      try:
        print(f"Requesting {row['URL']}")
        page = requests.get(row['URL']).text
        row["meta_description"] = get_meta_description(page)

        # what else?
        out.writerow(row)
      except:
        print(f"Failure with {row['URL']}. Skipping.")
        pass

