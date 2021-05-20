"""Data models for the API.
"""

from enum import IntEnum
from tortoise.models import Model
from tortoise import fields


class RelationshipStatus(IntEnum):
  """Enumeration representing the status of a relationship
  """

  NONE = 0
  PENDING = 1
  ACCEPTED = 2
  DECLINED = 3
  BLOCKED = 4
  ME = 5


class Relationship(Model):
  """Relationship model
  """

  author_one_id = fields.CharField(max_length=40)
  author_two_id = fields.CharField(max_length=40)
  status = fields.SmallIntField()
  action_id = fields.CharField(max_length=40)

  class Meta:
    """Relationship metadata.
    """

    unique_together = ("author_one_id", "author_two_id")


class Quote(Model):
  """Quote model
  """

  id = fields.IntField(pk=True)
  body = fields.CharField(max_length=140)
  author = fields.CharField(max_length=40, null=True)
  published = fields.DatetimeField(auto_now_add=True)
  meanings: fields.ReverseRelation["Meaning"]

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

  class Meta:
    """Meaning metadata.
    """

    ordering = ["-published"]
