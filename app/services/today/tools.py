from datetime import date, datetime

from app.utils.redis import Redis
from app.services.quotes.models import Quote


async def fetch_in_background(day: date, user_id: str) -> None:
  """Continuously fetch fresh quotes in the background.
  """

  redis = Redis().connection
  today = datetime.utcnow().date()
  daystring = day.isoformat()

  await redis.set(f"today:background:{user_id}", "true")

  # While it's still today...
  while today <= day:

    # Have we seen all available quotes?
    num_quotes = await redis.scard(f"today:{daystring}:quotes")
    num_seen = await redis.scard(f"today:{daystring}:seen:{user_id}")
    submitted = await redis.exists(f"today:{daystring}:user:{user_id}")
    offset = 2 if submitted else 1
    if num_seen >= num_quotes - offset:
      break

    # Get some quotes.
    quotes = await redis.srandmember(f"today:{daystring}:quotes", count=2)

    # Determine if noe of the quotes was written by the user.
    quote_a = await Quote.filter(id=quotes[0]).first()
    quote_b = await Quote.filter(id=quotes[1]).first()
    authored = user_id == quote_a.author_id or user_id == quote_b.author_id

    # If we haven't seen either of those quotes yet, use them!
    # Also if the user isn't the author of the quote.
    has_seen_a = await redis.sismember(
      f"today:{daystring}:seen:{user_id}",
      quotes[0],
    )
    has_seen_b = await redis.sismember(
      f"today:{daystring}:seen:{user_id}",
      quotes[1],
    )
    if not has_seen_a and not has_seen_b and not authored:
      await redis.sadd(f"today:{daystring}:request:{user_id}", *quotes)
      await redis.sadd(f"today:{daystring}:seen:{user_id}", *quotes)
      break

    # Otherwise, try again.
    today = datetime.utcnow().date()

  await redis.delete(f"today:background:{user_id}")
  return
