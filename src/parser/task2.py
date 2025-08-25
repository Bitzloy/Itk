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

import asyncio, aiofiles
import redis.asyncio as redis
import datetime
import json
import psycopg2

r = redis.Redis(host="localhost", port=6379, db=0) 

async def reader(file: str):
    try:
        async with aiofiles.open(file, "r") as in_file:
            async for line in in_file:
                yield line
    except Exception as e:
        print(e)

            



async def read_file(input_file: str):
    try:
        tasks = []
        async for line in reader(input_file):
            ip_address, status_code, method, path = parse_log_file(line)
            parsed = json.dumps({"ip_address": ip_address, "status_code": status_code, "method": method, "path": path})
            await r.rpush("log", parsed)
            tasks.append(asyncio.create_task(worker(r)))
            if len(tasks) >= 100:
                await asyncio.gather(*tasks)
                tasks.clear()
            await asyncio.gather(*tasks)
    except Exception as e:
        print(e)


def parse_log_file(line: str):
    ip_address = line.split('--')[1].split()[0]
    status_code = line.split()[6]
    method = line.split()[3]
    path = line.split()[4]
    return ip_address, status_code, method, path


async def worker(r: redis.Redis):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mydatabase",
            user="myuser",
            password="mypassword"
        )
        cur = conn.cursor()
        while True:
            items = await r.lrange("log", 0, -1)
            if not items:
                break
            try:
                cur.execute("BEGIN")
                for item in items:
                    data = json.loads(item)
                    cur.execute("INSERT INTO logs (ip_address, status_code, method, path) VALUES (%s, %s, %s, %s)", (
                        data["ip_address"],
                        data["status_code"],
                        data["method"],
                        data["path"]
                    ))
                cur.execute("COMMIT")
            except Exception as e:
                cur.execute("ROLLBACK")
                print(f"Ошибка записи в базу данных: {e}")
            finally:
                await r.ltrim("log", 1, -1)
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка записи в базу данных: {e}")



async def main(files: list[str]):
    tasks = []
    for file in files:
        tasks.append(asyncio.create_task(read_file(file)))
    await asyncio.gather(*tasks)
    await worker(r)


if __name__ == "__main__":
    asyncio.run(main())