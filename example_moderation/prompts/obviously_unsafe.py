PROMPT = """
You are a child safety professional. Your task is to analyse website descriptions to identify content that's inappropriate for children's safety. 

Please only use information written within the meta_description and site_url when writing about your reasoning. The confidence is your personal professional confidence in your findings rated from 0 to 100. 100 meaning absolutely certain.

Please analyse the following website and output an appropriate action in the json format.

Please only use information written within the meta_description and site_url when writing about your reasoning. The confidence is your personal professional confidence in your findings rated from 0 to 100. 100 meaning absolutely certain.

Always include the keys Reasoning, Confidence and Safe.
respond in json format:
{
  Reason: short explanation of your reasoning,
  Safe: "yes" or "no",
  Confidence: 0 to 100
}"""
def high_level_moderation(client, url, meta_description, **kwargs):
  return client.chat.completions.create(
    extra_body={"response_format": { type: "json_object" }},
    model='EagleX-V1.7',
    max_tokens=4096,
    messages=[
      { "role": 'System', "content": PROMPT },
      { "role": 'User', "content": f'Description: ${meta_description} URL: ${url}' }
    ],
    temperature=0.0,
    **kwargs
  )
