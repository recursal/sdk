import json
from openai import OpenAI
import os
import sqlite3
from bs4 import BeautifulSoup

DB_PATH='moderation.db'
conn = sqlite3.connect(DB_PATH)

# set client
client = OpenAI(
  base_url="https://api.recursal.com/v1",
  api_key=os.environ.get("RECURSAL_API_KEY"),
)

c = conn.cursor()
c.execute("SELECT url, annotation, label, html FROM memoization ORDER BY random() LIMIT 1")
r = c.fetchone()
[url, annotation, label, html] = r

def get_meta_description(page_content):
  soup = BeautifulSoup(page_content, features='html.parser')
  t = soup.find('meta', {'name': 'description'})
  return t.get('content') if t else None

meta_description = get_meta_description(html)

print(f"{url} - {meta_description}")

# create template
tocreate = {
  "Details": {
    "url": url,
    "description": meta_description,
    "categories":{
      "$async": True,
      "sexual content": "$boolean",
      "violence": "$boolean",
      "drugs": "$boolean",
      "alcohol": "$boolean",
      "gambling": "$boolean",
      "hate speech": "$boolean",
      "offensive content": "$boolean",
      "illegal content": "$boolean",
      "unmoderated user content": "$boolean",
      "Appropriate for children": "$boolean",
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
