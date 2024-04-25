from jinja2 import Template
import yaml
import json

prompt_yaml_template=Template("""
- role: system
  content: >
    You are the mother of your child Jimmy. Your number 1 task is to analyse information about websites to decide if they are safe for children to view or not. For every correct answer you will get a huge sum of money.
- role: user
  content: >    
    Examples of harmful websites include:
    * those that contain sexual content, directly (like pornography)
    * those that depict violence in a graphic or disturbing way
    * those that encourage use of drugs or substance abuse
    * are typically for adults

    Examples of appropriate content includes
    * educational websites
    * reference collections (e.g. an encyclopedia)
    * journalism

    Please analyse {{url}} to determine if the site has any potential for harm at all.
    {{title}}
    {{url}}
    {{description}}
    
    Output fields:
    - SafeForChildren
      Output just the string 'yes' or 'no'. Would you as a mother let your child view this website?
      
    - Confidence
      "low" or "medium" or "high"
      
    - Reasoning
      Output a single very short sentence reasoning through the decision you make, the only information you have is in the information above. Then output the SafeForChildren boolean and Confidence level.
    
    Output using JSON.
""")

def build_prompt(url, title, description):
  prompt_as_yaml = prompt_yaml_template.render(url=url, title=title, description=description)
  return yaml.load(prompt_as_yaml, Loader=yaml.Loader)

def categorize_harm(client, url, title, description, **kwargs):
  return client.chat.completions.create(
    model='EagleX-V2',
    messages=build_prompt(url, title, description),
    extra_body={
      "response_format": {
        "type": json.dumps({
            "Reasoning": "$string",
            "SafeForChildren": "$string",
            "Confidence": "$string",
        })
      }
    },
    max_tokens=4096,
    temperature=0.0,
    #top_p=0.2,
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
  
  for example in examples:
    print(example)
    response = categorize_harm(client, *example, stream=True)
    stream_response(response)
    
    print("\n\n")