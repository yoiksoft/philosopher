"""Data transfer objects.
"""

import typing
from app.models import Quote, Relationship, RelationshipStatus


async def get_quotes_from(
  author: str,
  offset: int = 0,
  count: int = 10,
) -> typing.Iterable[Quote]:
  """Get quotes written by an author.
  """

  if not author:
    raise TypeError("Missing argument 'author'")

  quotes: typing.Iterable[Quote] = await Quote \
    .filter(author=author) \
    .offset(offset) \
    .limit(count)

  return quotes


async def get_relationship_between(
  author_a: str,
  author_b: str,
) -> RelationshipStatus:
  """Check the relationship status between two users.
  """

  if not author_a:
    raise TypeError("Missing argument 'author_a'")

  if not author_b:
    raise TypeError("Missing argument 'author_b'")

  first = author_a if author_a < author_b else author_b
  second = author_a if author_a > author_b else author_b

  relationship: Relationship = await Relationship \
    .filter(author_one_id=first, author_two_id=second) \
    .first()

  if not relationship:
    return RelationshipStatus.NONE

  return RelationshipStatus(relationship.status)
