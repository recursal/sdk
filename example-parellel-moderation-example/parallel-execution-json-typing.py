import json
import time
from openai import OpenAI
import os
import bs4


client = OpenAI(
  base_url="https://api.recursal.com/v1",
  api_key=os.environ.get('RECURSAL_API_KEY')
)


# load the file
sample_data_file = os.path.join(os.path.dirname(__file__), "Human_body.html")
with open(sample_data_file) as inf:
    txt = inf.read()
    soup = bs4.BeautifulSoup(txt, features="html.parser")

otags = soup.findAll("p")

tags = [tag for tag in otags if tag.get_text() and len(tag.get_text().strip()) != 0]
    

print(tags[0].string)
print(tags[0].name)
print(tags.__len__())
taggs =  ",\n".join([
        """"tag_"""+str(i)+"""": SyncDict({"Content of tag":" """+tag.get_text().replace('\"',"").replace('string',"String").replace('number',"Number").replace('"',"").replace("\n", "\\n")+""" ",
        "violence":boolean,
        "level of violence":number,
        "sexual content":boolean,
        "level of sexual content":number,
        "block":boolean
        })"""
      for i, tag in enumerate(tags)])
      
jsonout = """
SyncDict({
  "Unsafe objects": number,
  "tags": AsyncDict({
    """ + taggs + """
  })
})
"""
  
response = client.chat.completions.create(
  model='EagleX-V2',
  messages=[
    {"role": "system", "content": "Please check this webpage for content unsuitable for child"},
    {"role": "user", "content": "Please send an email to jill to let her know that the report is ready"},
    {
      "role": "page",
      "content": str(soup.get_text())
    },
    {
      "role": "user",
      "content": "Please show the sexual content of the provided tag"
    }
    ],
  max_tokens=500,

  temperature=0.0,
  extra_body={
    "response_format":{
        "type": jsonout
    }
  },
  top_p=0.5,
  stream=True
)
tokensgenerated = 0
generated = ""
for message in response:
  # print(message.choices[0].text, end="", flush=True)
  print(message.choices[0].delta.content, end="", flush=True)
  tokensgenerated += 1
  generated += message.choices[0].delta.content if message.choices[0].delta.content else ""

# otime = time.time()

generated = generated.replace("\n","")

import json


try:
  objects = json.loads(generated)
  
  for i, tag in enumerate(tags):
    violent = objects["tags"]["tag_"+str(i)]["violence"]
    amount = objects["tags"]["tag_"+str(i)]["level of violence"]
    sexual = objects["tags"]["tag_"+str(i)]["sexual content"]
    samount = objects["tags"]["tag_"+str(i)]["level of sexual content"]
      
    tag.wrap(soup.new_tag("div", style="background-color: "+('#ff6666' if sexual else '#66ff66')))
      

  with open("edited_file.html", "w") as outf:
    outf.write(str(soup))
  
  with open("edited_stuff.html", "w") as outf:
    outf.write(str(otags))
  
except Exception as e:
  print(e)
  
  with open("edited_file.json", "w") as outf:
   outf.write(generated)
