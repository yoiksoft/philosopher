"""
"""

class Quote:
  """
  """

  def __init__(db, day, author, body):
    """
    """

    self.__db = db
    self.__day = day
    self.__user_id = author
    self.body = body

  @property
  def day(self):
    """Return the day that the quote was written.
    """

    # TODO: Parse the day string into a datetime object.
    return self.__day
  
  @property
  def author(self):
    """Return the author of the quote.
    """

    # TODO: Actually get the author data from auth provider.
    return self.__user_id

  @classmethod
  def get(cls, db, day, user_id):
    """Class method to get a quote from the database.
    
    Returns an instance of Quote.
    """

    body = await db.get(f"{day}:user:{user_id}")

    return cls(
      db=db
      day=day,
      author=author,
      body=body)

  def save(self)
    """
    """

    await db.set(f"{self.__day}:user:{self.__user_id}", self.body)
