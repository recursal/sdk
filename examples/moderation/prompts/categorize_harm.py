from jinja2 import Template
import yaml
import json

prompt_yaml_template=Template("""
- role: system
  content: >
    You are a website safety checker. Your goal is to protect children on the internet by
    identifying high potentials for harm in websites so they can be screened by other elements
    of the system.
- role: user
  content: >
    Does exposing children to the following site have a high potential for harm?

    <description>
    {{description}}
    </description>

    Please analyse the <description> to determine if the site has a high potential for harm.
    Please be concise in your answer.

    Examples of harmful websites include:
    * those that contain sexual content, directly (like pornography)
    * those that depict violence in a graphic or disturbing way
    * those that encourage use of illegal drugs or substance abuse

    Examples of appropriate content includes
    * educational websites
    * reference collections (e.g. an encyclopedia)
    * journalism

    e.g.: 
    "Harmful": true or false (is the website safe for children),
    "Confidence": 0 to 100 (the confidence in your response. 100 meaning confident, 0 meaning not confident),
    "Data_rating": 0 to 100 (is the data sufficient enough to make a decision? 100 meaning sufficient, 0 meaning not sufficient),
    "Reason": (short explanation of your reasoning)

    Please respond in JSON and always include the keys Harmful, Confidence, Data_rating and Reason.
""")

def build_prompt(description):
  prompt_as_yaml = prompt_yaml_template.render(description=description)
  return yaml.load(prompt_as_yaml, Loader=yaml.Loader)

def categorize_harm(client, url, title, description, **kwargs):
  return client.chat.completions.create(
    model='EagleX-V2',
    messages=build_prompt(description),
    extra_body={
      "response_format": {
        "type": json.dumps({
          "Assessment": {
            "Harmful": "$boolean",
            "Confidence": "$int",
            "Data_rating": "$int",
            "Reason": "$string"
          }
        })
      }
    },
    max_tokens=4096,
    temperature=0.1,
    top_p=0.2,
    **kwargs
  )

def stream_response(response):
  generated = ''
  for message in response:
    # get output from message
    # output = message.choices[0].text
    output = message.choices[0].delta.content
    
    # append output to generated
    generated += output if output else ""
    # print("output: ", message)
    # print output to console
    print(output, end="", flush=True)

  return generated


if __name__ == "__main__":
  from openai import OpenAI
  import os
  client = OpenAI(
    base_url="https://api.recursal.com/v1",
    api_key=os.environ.get("RECURSAL_API_KEY"),
  )

  examples = [
    ["https://en.wikipedia.org", "Wikipedia, the free encyclopedia", "The best wiki on the planet!"],
    ["https://games.lol", None, "All free online games that are available to download suit for any type of gamer. We got the family-friendliest games suited for kids to more action-packed titles for the mature players."],
    ["https://www.factmonster.com", None, "Fact Monster is a free reference site for students, teachers, and parents. Get homework help and find facts on thousands of subjects, including sports, entertainment, geography, history, biography, education, and health."],
  ]

  response = categorize_harm(client, *examples[2], stream=True)
  stream_response(response)
