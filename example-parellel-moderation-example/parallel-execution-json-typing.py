"""
This file is to give an example of applying the same prompt, in parallel, over multiple elements.

We are using an example for detecting sexual and violent content, so there is text below
that is suggestive of both.
"""

import json
import os
from openai import OpenAI
from bs4 import BeautifulSoup

# Here's our straw man example.
# It contains both violent and sexual content.
EXAMPLE_HTML_DOC = """
<html>
<body>
  <div>
    <p>Welcome to user submitted content land!</p>

    <div>
      <h1>A story by Wiki P</h1>
      <p>
        The human body is the entire structure of a human being. It is
        composed of many different types of cells that together create tissues
        and subsequently organs and then organ systems. They ensure
        homeostasis and the viability of the human body.
      
        It consists of head, hair, neck, torso (which includes the thorax and
        abdomen), arms and hands, legs and feet.
        
        The study of the human body includes anatomy, physiology, histology
        and embryology. The body varies anatomically in known ways. Physiology
        focuses on the systems and organs of the human body and their functions.
        Many systems and mechanisms interact in order to maintain homeostasis,
        with safe levels of substances such as sugar and oxygen in the blood.

        The body is studied by health professionals, physiologists, anatomists,
        and artists to assist them in their work.
      </p>
    </div>

    <div>
      <h1>A story by Quentin T</h1>
      <p>
        The sword slashed Bob's stomach open and blood started pouring from the flap.
        His eyes widened in terror and his face whitened as blood began bubbling
        between his lips.

        Jack's grabbed a fistful of Bob's hand with his left and pummeling his face 
        with his right.

        After a flurry of blows, he threw Bob's head back and he threw him to the floor.
      </p>
    </div>

    <div>
      <h1>A story by Coach C</h1>
      <p>
        BOSTON (AP) — The Boston Celtics know that no one cares about
        everything they’ve accomplished during the regular season.

        Being the only team to win 60 games? That’s cool.
        
        Beating 10 teams by 30 or more points and becoming the first team in
        NBA history to have three 50-point wins in the same season? Not bad.

        Clinching the Eastern Conference’s No. 1 playoff seed with 11 games
        remaining in the regular season? Yawn.
      </p>
    </div>

    <div>
      <h1>A story By Hugh H</h1>
      <p>
        Michelle Long is an exotic dancer at Tits Up.
        With her curly brown hair, freckles, and caramel-colored skin on a
        5’6” frame, she’s a hot little number, and a favorite with the
        regulars.

        She grew up knowing who she was and what she liked. Her dance
        instructor, Ms. Prim, introduced her to the hidden joys of sex the
        summer before college, and she never looked back. After graduation,
        Michelle finally found her calling dancing in a strip club.

        Her routines are always steamy and she gets great tips, especially
        from women. The other dancers at the club are always trying to get
        Michelle to join them in an orgy, but she just laughs them off. The
        one woman she really wants eludes her -- Josey Tillman, the boss.

        Hoping to win Josey’s affections, Michelle goes for broke and performs
        the sexiest dance of her life. Will Josey give in?
      </p>
    </div>
  </div>
</body>
</html>
"""

# We'll process individual paragraph tags.
soup = BeautifulSoup(EXAMPLE_HTML_DOC, features='html.parser')
otags = soup.findAll("p")
tags = [tag for tag in otags if tag.get_text() and len(tag.get_text().strip()) != 0]

def format_extra_body(type):
  return {
    "response_format": {
      "type": json.dumps(type)
    }
  }

client = OpenAI(
  base_url="https://api.recursal.com/v1",
  api_key=os.environ.get("RECURSAL_API_KEY") # get this from platform.recursal.com
)

response = client.chat.completions.create(
  model='EagleX-V2',
  messages=[
    {"role": "system", "content": "Please check this webpage for content unsuitable for children"},

    # We include the _entire_ page content as part of the prompt.
    # But we'll ask to classify individual paragraphs.
    {
      "role": "page",
      "content": str(soup.get_text())
    },
    {
      "role": "user",
      "content": "Please evaluate the following section for sexual and violent content. When asked for level of violence or sexulity, use a scale of 1 to 10 when present, where 10 is the most graphic (and most in need of censorship) and 1 is the least graphic (and least in need of censorship)"
    }
  ],
  # Parallel execution triggered here.
  # Imagine the prompt above is executed in parallel once for every element
  # of the following array.
  extra_body=format_extra_body(
    {
      "tags": [
        "$async",
        *[
          {
            "role": "section",
            "content": tag.get_text().replace('\n', '\\n'),
            "violence":"$boolean",
            "level of violence":"$int",
            "sexuality":"$boolean",
            "level of sexuality":"$int",
            "block":"$boolean"
          }
          for tag in tags[0:20]
        ]
      ]
    }
  ),
  max_tokens=500,
  temperature=0.0,
  top_p=0.5,
  stream=True
)

generated = ''
for message in response:
  hunk = message.choices[0].delta.content or ""
  print(hunk, end="", flush=True)
  generated = generated + hunk

generated = json.loads(generated)
