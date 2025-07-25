import concurrent.futures
import csv
import json
import multiprocessing
import multiprocessing.pool
import random
import time
from math import factorial
from multiprocessing import Process, Queue, cpu_count


def generate_data(n: int) -> list[int]:
    data = []
    for _ in range(n):
        data.append(random.randint(1, n))
    return data


def process_number(number):
    return factorial(number)


data = generate_data(100)


def with_thread_pool(data: list[int]) -> list[int]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return list(executor.map(process_number, data))


# print(with_thread_pool(data))


def with_multiprocess_pool(data: list[int]) -> list[int]:
    with multiprocessing.Pool(processes=cpu_count()) as pool:
        return pool.map(process_number, data)


# print(with_multiprocess_pool(data))


def worker(input_queue, output_queue):
    while True:
        number = input_queue.get()
        if number is None:
            break
        result = process_number(number)
        output_queue.put(result)


def process_with_custom_processes(data):
    input_queue = Queue()
    output_queue = Queue()

    num_workers = cpu_count()
    processes = []

    for _ in range(num_workers):
        p = Process(target=worker, args=(input_queue, output_queue))
        p.start()
        processes.append(p)

    for number in data:
        input_queue.put(number)

    for _ in processes:
        input_queue.put(None)

    results = [output_queue.get() for _ in data]

    for p in processes:
        p.join()

    return results


def process_single_thread(data):
    return [process_number(n) for n in data]


def benchmark(data):
    results = {}

    for name, func in [
        ("Single-threaded", process_single_thread),
        ("ThreadPoolExecutor", with_thread_pool),
        ("MultiprocessingPool", with_multiprocess_pool),
        ("CustomProcesses", process_with_custom_processes),
    ]:
        start = time.time()
        output = func(data)
        duration = time.time() - start
        results[name] = duration

        with open(f"result_{name}.json", "w") as f:
            json.dump(output, f)

    return results


if __name__ == "__main__":
    data = generate_data(100)

    timings = benchmark(data)

    with open("timings.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Method", "Duration (seconds)"])
        for method, duration in timings.items():
            writer.writerow([method, duration])

    for method, duration in timings.items():
        print(f"{method}: {duration:.2f} seconds")
