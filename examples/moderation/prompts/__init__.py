from .categorize_harm import categorize_harm

class Moderator:
  @classmethod
  def categorize_harm(cls, client, *args, **kwargs):
    return categorize_harm(client, *args, **kwargs)

