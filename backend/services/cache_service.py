import redis
import json
from typing import Optional, Any
from config import settings

class CacheService:
    """Simple Redis cache for storing analysis results."""
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            self.redis_client.ping()
            print("✅ Redis cache connected")
        except Exception as e:
            print(f"⚠️  Redis cache not available: {e}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(f"pullsense:{key}")
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, expire: int = 3600):
        """Set value in cache with expiration (default 1 hour)."""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                f"pullsense:{key}",
                expire,
                json.dumps(value)
            )
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete value from cache."""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.delete(f"pullsense:{key}")
        except Exception as e:
            print(f"Cache delete error: {e}")

# Singleton instance
cache = CacheService()