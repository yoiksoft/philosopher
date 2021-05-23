"""Data models for the API.
"""

from tortoise.models import Model
from tortoise import fields


class Author:
  """Simple Python model representing an author.
  """

  def __init__(
    self,
    user_id: str,
    username: str,
    picture: str,
  ):
    self.user_id = user_id
    self.username = username
    self.picture = picture

  async def to_dict(self):
    """Serialize into dictionary.
    """

    return {
      "user_id": self.user_id,
      "username": self.username,
      "picture": self.picture,
    }


class Quote(Model):
  """Quote model
  """

  id = fields.IntField(pk=True)
  body = fields.CharField(max_length=140)
  author = fields.CharField(max_length=40, null=True)
  published = fields.DatetimeField(auto_now_add=True)
  meanings: fields.ReverseRelation["Meaning"]

  async def to_dict(self):
    """Serialize into dictionary.
    """

    return {
      "id": self.id,
      "body": self.body,
      "author": self.author,
      "published": self.published.isoformat(),
    }

  class Meta:
    """Quote metadata.
    """

    ordering = ["-published"]


class Meaning(Model):
  """Meaning model
  """

  id = fields.IntField(pk=True)
  body = fields.CharField(max_length=240)
  author = fields.CharField(max_length=40, null=True)
  quote: fields.ForeignKeyRelation[Quote] = fields.ForeignKeyField(
    model_name="models.Quote", related_name="meanings", on_delete="CASCADE")
  published = fields.DatetimeField(auto_now_add=True)

  async def to_dict(self):
    """Serialize into dictionary.
    """

    await self.fetch_related("quote")

    return {
      "id": self.id,
      "body": self.body,
      "author": self.author,
      "quote": self.quote.id,  # pylint: disable=no-member
      "published": self.published.isoformat(),
    }

  class Meta:
    """Meaning metadata.
    """

    ordering = ["-published"]
