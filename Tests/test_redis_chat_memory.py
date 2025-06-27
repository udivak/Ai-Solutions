import sys
import types
import pytest
import asyncio
from pathlib import Path

# Provide a stub redis.asyncio module so redis_chat_memory can be imported
class _DummyRedis:
    def __init__(self):
        self.store = {}

    async def hset(self, key, mapping=None, **kwargs):
        if mapping:
            self.store.setdefault(key, {}).update(mapping)

    async def expire(self, key, ttl):
        pass

    async def hgetall(self, key):
        return self.store.get(key, {})

    async def delete(self, key):
        self.store.pop(key, None)

# Install stub before importing the module under test
_dummy = _DummyRedis()
redis_asyncio = types.ModuleType("redis.asyncio")
redis_asyncio.Redis = lambda **kwargs: _dummy
parent = types.ModuleType("redis")
parent.asyncio = redis_asyncio
sys.modules.setdefault("redis", parent)
sys.modules.setdefault("redis.asyncio", redis_asyncio)

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DB import redis_chat_memory

@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    # Ensure functions use the dummy redis instance
    monkeypatch.setattr(redis_chat_memory, "r", _dummy)
    _dummy.store.clear()
    yield _dummy

def test_store_single_item(fake_redis):
    asyncio.run(redis_chat_memory.store_order_items("123", {"item_name": "apple", "quantity": 2}))
    result = asyncio.run(redis_chat_memory.get_order_items("123"))
    assert result == {"apple": 2}

def test_store_multiple_items(fake_redis):
    items = [
        {"item_name": "banana", "quantity": 3},
        {"item_name": "orange", "quantity": 1},
    ]
    asyncio.run(redis_chat_memory.store_order_items("456", items))
    result = asyncio.run(redis_chat_memory.get_order_items("456"))
    assert result == {"banana": 3, "orange": 1}
