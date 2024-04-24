import json
from openai import OpenAI
import os
import csv
from bs4 import BeautifulSoup
from .test_cases import get_db_connection
from .prompts import Moderator

# set client
client = OpenAI(
  base_url="https://api.recursal.com/v1",
  api_key=os.environ.get("RECURSAL_API_KEY"),
)

def get_title(soup):
  t = soup.find('title')
  return t.get('content') if t else None

def get_description(soup):
  t = soup.find('meta', {'name': 'description'})
  return t.get('content') if t else None

if __name__ == "__main__":
  with get_db_connection() as conn, open('moderation-results.csv', 'w') as outfile:
    csv = csv.writer(outfile)
    csv.writerow(["URL", "title", "description", "Reason", "Harmful", "Confidence"])

    c = conn.cursor()
    c.execute("SELECT url, annotation, label, html FROM memoization")

    for row in c.fetchall():
      [url, annotation, label, html] = row
      soup = BeautifulSoup(html, features='html.parser')
      title = get_title(soup)
      description = get_description(soup)

      print(f"{url} - {title} - {description}")

      stream = True
      if stream:
        response = Moderator.categorize_harm(client, url, title, description, stream=True)

        generated = ""
        for message in response:

          # get output from message
          output = message.choices[0].delta.content
          # output = message.choices[0].delta["content"]
          
          # append output to generated
          generated += output if output else ""
          # print("output: ", message)
          # print output to console
          print(output, end="", flush=True)
      else:
        response = Moderator.categorize_harm(client, url, title, description)
        generated = response.choices[0].message.content
        print(generated)


      try:
        generated = json.loads(generated)
        csv.writerow([url, title, description, *[v for v in generated.values()]])
      except Exception as e:
        print(f"JSON parsing failure: {e}")
