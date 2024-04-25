import json

CATEGORIES = [
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

def categorize_site(client, url, meta_description, **kwargs):
    #perform completion
    return client.chat.completions.create(
      model='EagleX-V2',
      prompt="",
      max_tokens=500,
      temperature=0,
      extra_body={
        "response_format":{
            "type": json.dumps({
              "Details": {
                "url": url,
                "description": meta_description,
                "categories indicated in description":{
                  "$async": True,
                  **{ c: "$boolean" for c in CATEGORIES }
                }
              }
            })
        }
      },
      top_p=0.5,
      **kwargs
    )
