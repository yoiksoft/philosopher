from tortoise.models import Model
from tortoise import fields

from app.utils.auth import get_user


class Quote(Model):
  """Quote model
  """

  id = fields.IntField(pk=True)
  body = fields.CharField(max_length=140)
  author_id = fields.CharField(max_length=40)
  published = fields.DatetimeField(auto_now_add=True)

  async def to_dict(self):
    return {
      "id": self.id,
      "body": self.body,
      "published": str(self.published)
    }

  async def get_author(self):
    """Get rich data about a quote's author.
    """

    return await get_user(self.author_id)
  
  class Meta:
    ordering = ["-published"]