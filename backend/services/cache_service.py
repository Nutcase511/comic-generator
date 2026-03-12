"""
简单的内存缓存服务
用于缓存频繁访问的数据，减少数据库查询
"""
import time
import json
from typing import Any, Optional, Dict, Callable
from functools import wraps
from loguru import logger


class CacheService:
    """简单的内存缓存服务"""

    def __init__(self):
        self._cache: Dict[str, tuple[Any, float]] = {}  # {key: (value, expiry_time)}
        self._default_ttl = 300  # 默认缓存5分钟

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            else:
                # 缓存过期，删除
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        ttl = ttl or self._default_ttl
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)
        logger.debug(f"缓存已设置: {key}, TTL: {ttl}秒")

    def delete(self, key: str) -> None:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"缓存已删除: {key}")

    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        logger.debug("所有缓存已清空")

    def cleanup_expired(self) -> None:
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if current_time >= expiry
        ]
        for key in expired_keys:
            del self._cache[key]
        if expired_keys:
            logger.debug(f"清理了 {len(expired_keys)} 个过期缓存")


# 全局缓存实例
cache_service = CacheService()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    缓存装饰器

    Args:
        ttl: 缓存时间（秒），默认300秒
        key_prefix: 缓存键前缀
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # 尝试从缓存获取
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result

            # 缓存未命中，执行函数
            result = await func(*args, **kwargs)

            # 存入缓存
            cache_service.set(cache_key, result, ttl)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步函数版本
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result

            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            return result

        # 根据函数类型返回对应的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
