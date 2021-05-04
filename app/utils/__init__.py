"""Application utilities

Functions and classes to help the application.
"""

from starlette.config import Config


# Starlette helper class to load configurations from an environment file.
config: Config = Config(".env")


class Singleton(object):
  """Singleton class to ensure only one instance of a subclass exists.
  """

  def __new__(cls, *args, **kwargs):
    """Override creating new singleton to prevent multiple instances.
    """

    it = cls.__dict__.get("__it__")
    if it is not None:
      return it
    cls.__it__ = it = object.__new__(cls)
    it.init(*args, **kwargs)
    return it

  def init(self, *args, **kwargs):
    """Custom init method due to issues with __init__
    """

    pass
