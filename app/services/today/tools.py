from datetime import date

from app.utils.redis import Redis

async def fetch_in_background(day: date, user_id: str) -> None:
  """Continuously fetch fresh quotes in the background.
  """

  redis = Redis().connection
  today = date.today()
  daystring = day.isoformat()

  await redis.set(f"today:background:{user_id}", True)

  # While it's still today...
  while today <= day:

    # Have we seen all available quotes?
    num_quotes = await redis.scard(f"today:{daystring}:quotes")
    num_seen = await redis.scard(f"today:{daystring}:seen:{user_id}")
    if num_seen >= num_quotes - 1:
      break
    
    # Get some quotes.
    quotes = await redis.srandmember(f"today:{daystring}:quotes", count=2)

    # If we haven't seen either of those quotes yet, use them!
    has_seen_a = await redis.sismember(f"today:{daystring}:seen:{user_id}", quotes[0])
    has_seen_b = await redis.sismember(f"today:{daystring}:seen:{user_id}", quotes[1])
    if not has_seen_a and not has_seen_b:
      await redis.sadd(f"today:{daystring}:request:{user_id}", *quotes)
      await redis.sadd(f"today:{daystring}:seen:{user_id}", *quotes)
      break
    
    # Otherwise, try again.
    today = date.today()

  await redis.delete(f"today:background:{user_id}")
  return
