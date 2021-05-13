"""Application utilities

Functions and classes to help the application.
"""

from starlette.config import Config

# Starlette helper class to load configurations from an environment file.
config: Config = Config(".env")


class Singleton:
  """Singleton class to ensure only one instance of a subclass exists.
  """

  def __new__(cls, *args, **kwargs):
    """Override creating new singleton to prevent multiple instances.
    """

    instance = cls.__dict__.get("__it__")
    if instance is not None:
      return instance
    cls.__it__ = instance = object.__new__(cls)
    instance.init(*args, **kwargs)
    return instance

  def init(self, *args, **kwargs):
    """Custom init method due to issues with __init__
    """
