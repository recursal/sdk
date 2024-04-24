import json
from openai import OpenAI
import os
import sqlite3
import csv
from bs4 import BeautifulSoup

DB_PATH='moderation.db'
conn = sqlite3.connect(DB_PATH)

# set client
client = OpenAI(
  base_url="https://api.recursal.com/v1",
  api_key=os.environ.get("RECURSAL_API_KEY"),
)

c = conn.cursor()

def get_meta_description(page_content):
  soup = BeautifulSoup(page_content, features='html.parser')
  t = soup.find('meta', {'name': 'description'})
  return t.get('content') if t else None

c.execute("SELECT url, annotation, label, html FROM memoization")
with open('moderation-results.csv', 'w') as outfile:
  categories = [
    "sexual content",
    "violence",
    "drugs",
    "alcohol",
    "gambling",
    "hate speech",
    "offensive content",
    "illegal content",
    "unmoderated user content",
    "Appropriate for children"
  ]

  csv = csv.writer(outfile)
  csv.writerow(["URL", "meta_description", *categories])

  for row in c.fetchall():
    [url, annotation, label, html] = row
    meta_description = get_meta_description(html)

    print(f"{url} - {meta_description}")

    # output template
    tocreate = {
      "Details": {
        "url": url,
        "description": meta_description,
        "categories indicated in description":{
          "$async": True,
          **{ c: "$boolean" for c in categories }
        }
      }
    }

    #perform completion
    response = client.completions.create(
      model='EagleX-V2',
      prompt="",
      max_tokens=500,
      temperature=0,
      extra_body={
        "response_format":{
            "type": json.dumps(tocreate)
        }
      },
      top_p=0.5,
      stream=True
    )

    generated = ""
    for message in response:

      # get output from message
      output = message.choices[0].text
      # output = message.choices[0].delta["content"]
      
      # append output to generated
      generated += output if output else ""
      # print("output: ", message)
      # print output to console
      print(output, end="", flush=True)

    try:
      generated = json.loads(generated)
      csv.writerow([url, meta_description, *[v for v in generated['Details']['categories indicated in description'].values()]])
    except Exception as e:
      print(f"JSON parsing failure: {e}")
