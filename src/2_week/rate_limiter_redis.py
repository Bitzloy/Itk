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
        current_count = self.redis.incr(self.key)
        if current_count == 1:
            self.redis.expire(self.key, self.interval)
        if current_count > self.limit:
            print("превышено количество запросов")
            return False
        else:
            print("Запрос разрешен")
            return True
        



def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


if __name__ == "__main__":
    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(0.1)

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
