# Пример лог-строки:
# IP-адрес - - [дата:время] "METHOD /path HTTP/1.1" статус-код размер_ответа "реферер" "user-agent".

# Задача — написать асинхронный скрипт на Python, который:
#    Асинхронно читает один или несколько больших лог-файлов (чтобы не блокировать основной поток и обрабатывать ввод-вывод эффективно).
#    Парсит каждую строку лога, извлекая ключевую информацию: IP-адрес, статус-код, метод запроса и путь.
#    Обрабатывает файлы потоково (line-by-line), без загрузки всего файла в память, чтобы избежать OutOfMemoryError на больших объемах.
#    Поддерживает обработку нескольких файлов параллельно (например, если переданы пути к нескольким логам).
#    Результат необходимо загрузить в PostgreSQL

# Ограничения:
#    Не используйте синхронные библиотеки вроде open() без asyncio.
#    Код должен работать на Python 3.10+.
#    Тестируйте на большом файле (кандидат может сгенерировать тестовый лог сам, например, с помощью скрипта).

import asyncio

import aiofiles
import asyncpg


async def reader(file: str):
    async with aiofiles.open(file, "r") as in_file:
        async for line in in_file:
            yield line


async def read_file(input_file: str, queue: asyncio.Queue):
    async for line in reader(input_file):
        ip_address, status_code, method, path = parse_log_file(line)

        await queue.put(
            {
                "ip_address": ip_address,
                "status_code": status_code,
                "method": method,
                "path": path,
            }
        )



def parse_log_file(line: str):
    ip_address = line.split("--")[1].split()[0]
    status_code = line.split()[6]
    method = line.split()[3]
    path = line.split()[4]
    return ip_address, status_code, method, path


async def worker(
    conn: asyncpg.Connection = None,
    queue: asyncio.Queue = None,
    batch_size: int = 100,
):
    batch = []
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        batch.append(
            (item["ip_address"], item["status_code"], item["method"], item["path"])
        )
        queue.task_done()

        if len(batch) >= batch_size:
            async with conn.transaction():
                await conn.executemany(
                    "INSERT INTO logs (ip_address, status_code, method, path) VALUES ($1, $2, $3, $4)",
                    batch,
                )
            batch.clear()
            

    if batch:
        async with conn.transaction():
            await conn.executemany(
                "INSERT INTO logs (ip_address, status_code, method, path) VALUES ($1, $2, $3, $4)",
                batch,
            )


async def main(files: list[str]):
    queue = asyncio.Queue()
    tasks = []
    conn = await asyncpg.connect(
        host="localhost", database="mydatabase", user="myuser", password="mypassword"
    )
    for file in files:
        tasks.append(asyncio.create_task(read_file(file, queue=queue)))

    workers = [asyncio.create_task(worker(queue = queue, conn = conn)) for _ in range(2)]

    await asyncio.gather(*tasks)
    await queue.join()

    for _ in workers:
        await queue.put(None)

    await asyncio.gather(*workers)

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main(["task2/log.log"]))
