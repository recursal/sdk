SYSTEM_PROMPT = """
You are educator. Your goal is to protect children on the internt by identifying high potentials for harm in websites
so they can be screened by other elements of the system.

Examples of harmful websites include:
 * those that contain sexual content, directly (like pornography)
 * those that depict violence in a graphic or disturbing way
 * those that encourage use of illegal drugs or substance abuse

Examples of appropriate content includes
 * educational websites
 * reference collections (e.g. )
 * journalism
"""

def build_user_prompt(url, title, description):
  return f"""
  Does exposing children to the following site have a high potential for harm?

  The URL is {url}
  The title of the webpage is {title if title else "(no title given)"}
  The webpage's description (of itself) is {description if description else "(no description given)"}

  Please respond in JSON and always include the keys Reasoning, Harmful and Confidence.
  e.g.:
  {{
    "Reason": (short explanation of your reasoning),
    "Harmful": "yes" or "no",
    "Confidence": 0 to 100
  }}

  Please be concise in your answer.

  Does that site have a high potential for harm?
  """

def gen_completion(url, title, description):
  return {
    "model": 'EagleX-V2',
    "messages": [
      { "role": 'System', "content": SYSTEM_PROMPT },
      { "role": 'User', "content": build_user_prompt(url, title, description) }
    ],
    "extra_body": {"response_format": { "type": "json_object" }},
    "max_tokens": 4096,
    "temperature": 0.0,
  }

def categorize_harm(client, url, title, description, **kwargs):
  return client.chat.completions.create(
    **gen_completion(url, title, description),
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
