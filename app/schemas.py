"""Schemas for request body.
"""

from typesystem import Schema, String


class QuoteSchema(Schema):
  """Schema for Quote body.
  """

  body = String(
    allow_blank=False,
    trim_whitespace=True,
    max_length=140,
    min_length=10,
  )


class MeaningSchema(Schema):
  """Schema for Meaning body.
  """

  body = String(
    allow_blank=False,
    trim_whitespace=True,
    max_length=240,
    min_length=10,
  )
