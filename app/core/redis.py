import redis.asyncio as redis
from app.core.config import settings


class RedisManager:
    def __init__(self):
        self.redis_client = None

    async def connect(self):
        """Connect to Redis."""
        self.redis_client = redis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )
        return self.redis_client

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str):
        """Get a value from Redis."""
        if not self.redis_client:
            await self.connect()
        return await self.redis_client.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        """Set a value in Redis with optional expiration."""
        if not self.redis_client:
            await self.connect()
        return await self.redis_client.set(key, value, ex=expire)

    async def delete(self, key: str):
        """Delete a key from Redis."""
        if not self.redis_client:
            await self.connect()
        return await self.redis_client.delete(key)

    async def exists(self, key: str):
        """Check if a key exists in Redis."""
        if not self.redis_client:
            await self.connect()
        return await self.redis_client.exists(key)


redis_manager = RedisManager()
