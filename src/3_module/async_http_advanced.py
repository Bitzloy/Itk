import asyncio
import json

import aiofiles
import aiohttp


async def fetch(
    session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, url: str
) -> dict:
    async with semaphore:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"url": url, "content": data}
                else:
                    return None

        except aiohttp.ClientConnectionError:
            return {"url": url, "status_code": -1}

        except (aiohttp.ServerTimeoutError, asyncio.TimeoutError):
            return {"url": url, "status_code": -2}

        except aiohttp.ClientResponseError as e:
            return {"url": url, "status_code": e.status}

        except aiohttp.ClientError:
            return {"url": url, "status_code": -3}

        except Exception:
            return {"url": url, "json_content": None}


async def fetch_urls(input_file: str, output_file: str):
    semaphore = asyncio.Semaphore(5)
    async with (
        aiohttp.ClientSession() as session,
        aiofiles.open(output_file, "a") as out_file,
    ):
        tasks = []

        async for url in read_urls(input_file):
            task = asyncio.create_task(fetch(session, semaphore, url))
            tasks.append(task)

            if len(tasks) >= 100:
                results = await asyncio.gather(*tasks)

                for result in results:
                    if result is not None:
                        await out_file.write(json.dumps(result) + "\n")

                tasks.clear()

        if tasks:
            results = await asyncio.gather(*tasks)
            for result in results:
                if result is not None:
                    await out_file.write(json.dumps(result) + "\n")


async def read_urls(in_file: str):
    async with aiofiles.open(in_file, "r") as file:
        async for url in file:
            yield url.strip()


if __name__ == "__main__":
    input_file = "urls.txt"
    output_file = "2_results.jsonl"

    asyncio.run(fetch_urls(input_file, output_file))
