import json

import redis


class RedisQueue:
    def __init__(self, name="default", host="localhost", port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db)
        self.key = f"queue:{name}"

    def publish(self, msg: dict):
        self.redis.rpush(self.key, json.dumps(msg))

    def consume(self) -> dict:
        item = self.redis.lpop(self.key)
        if item is not None:
            return json.loads(item)

        return None


if __name__ == "__main__":
    q = RedisQueue()
    q.publish({"a": 1})
    q.publish({"b": 2})
    q.publish({"c": 3})

    assert q.consume() == {"a": 1}
    assert q.consume() == {"b": 2}
    assert q.consume() == {"c": 3}
