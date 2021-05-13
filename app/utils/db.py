"""Database utilities.
"""

from app.utils import config

TORTOISE_ORM = {
  "connections": {
    "default": {
      "engine": "tortoise.backends.asyncpg",
      "credentials": {
        "host": config("DB_HOST"),
        "port": config("DB_PORT"),
        "user": config("DB_USER"),
        "password": config("DB_PASS"),
        "database": config("DB_NAME"),
      },
    },
  },
  "apps": {
    "models": {
      "models": ["app.services.quotes.models", "aerich.models"],
      "default_connection": "default",
    },
  },
}
