import datetime
import functools
import time

import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)


def single(max_processing_time: datetime.timedelta):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock_key = f"lock:{func.__name__}"
            lock = redis_client.lock(
                lock_key, timeout=max_processing_time.total_seconds(), blocking=False
            )

            got_lock = lock.acquire(blocking=False)
            if not got_lock:
                print(f"[{func.__name__}] Запуск заблокирован")
                return None

            try:
                print(f"[{func.__name__}] Запуск с локом.")
                return func(*args, **kwargs)

            finally:
                try:
                    lock.release()
                    print(f"[{func.__name__}] Лок снят.")

                except redis.TimeoutError:
                    print(f"[{func.__name__}] Лок уже истёк или снят.")

        return wrapper

    return decorator


@single(max_processing_time=datetime.timedelta(minutes=2))
def process_transaction():
    time.sleep(2)


for _ in range(10):
    process_transaction()
