"""Models for the Quotes and Meanings service.
"""

from tortoise.models import Model
from tortoise import fields

from app.utils.auth import get_user


class Quote(Model):
  """Quote model
  """

  id = fields.IntField(pk=True)
  body = fields.CharField(max_length=140)
  author_id = fields.CharField(max_length=40, null=True)
  published = fields.DatetimeField(auto_now_add=True)

  meanings: fields.ReverseRelation["Event"]

  async def to_dict(self):
    """Serialize the object into a dictionary.
    """

    return {
      "id": self.id,
      "body": self.body,
      "published": str(self.published),
    }

  async def get_author(self):
    """Get rich data about a quote's author.
    """

    return await get_user(self.author_id)

  class Meta:
    """Quote metadata.
    """

    ordering = ["-published"]


class Meaning(Model):
  """Meaning model
  """

  id = fields.IntField(pk=True)
  body = fields.CharField(max_length=240)
  author_id = fields.CharField(max_length=40, null=True)
  quote: fields.ForeignKeyRelation[Quote] = fields.ForeignKeyField(
    model_name="models.Quote", related_name="meanings", on_delete="CASCADE")
  published = fields.DatetimeField(auto_now_add=True)

  async def to_dict(self):
    """Serialize the object into a dictionary.
    """

    return {
      "id": self.id,
      "body": self.body,
      "published": str(self.published),
    }

  async def get_author(self):
    """Get rich data about a quote's author.
    """

    return await get_user(self.author_id)

  class Meta:
    """Meaning metadata.
    """

    ordering = ["-published"]
