import asyncio
import json

import aiofiles
import aiohttp

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
]


async def fetch(
    semaphore: asyncio.Semaphore, url: str, session: aiohttp.ClientSession
) -> dict:
    async with semaphore:
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return {"url": url, "status_code": response.status}

        except aiohttp.ClientConnectionError:
            return {"url": url, "status_code": -1}

        except (aiohttp.ServerTimeoutError, asyncio.TimeoutError):
            return {"url": url, "status_code": -2}

        except aiohttp.ClientResponseError as e:
            return {"url": url, "status_code": e.status}

        except aiohttp.ClientError:
            return {"url": url, "status_code": -3}

        except Exception:
            return {"url": url, "status_code": 0}


async def fetch_urls(urls: list[str], file_path: str):
    semaphore = asyncio.Semaphore(5)
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(asyncio.create_task(fetch(semaphore, url, session)))
        # tasks = [fetch(semaphore, url, session) for url in urls]
        results = await asyncio.gather(*tasks)

    async with aiofiles.open(file_path, "w") as file:
        for result in results:
            await file.write(json.dumps(result) + "\n")


if __name__ == "__main__":
    asyncio.run(fetch_urls(urls, "./results.jsonl"))
