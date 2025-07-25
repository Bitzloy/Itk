import random
import time
import uuid

import redis


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def __init__(self, key="rate_limiter", limit=5, interval=3):
        self.redis = redis.Redis(host="localhost", port=6379, db=0)
        self.key = key
        self.limit = limit
        self.interval = interval

    def test(self) -> bool:
        now = time.time()
        pipeline = self.redis.pipeline()

        pipeline.zremrangebyscore(self.key, 0, now - self.interval)
        pipeline.zadd(self.key, {str(uuid.uuid4()): now})
        pipeline.zcard(self.key)

        _, _, current_count = pipeline.execute()

        return current_count <= self.limit


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


if __name__ == "__main__":
    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(random.randint(1, 2))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
