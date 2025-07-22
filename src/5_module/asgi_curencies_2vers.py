import asyncio
import json
from urllib import error, request

"""
Каждая влюта вызывает json со списком всех валют отсносительно себя
"""


async def app(scope, receive, send):
    if scope["type"] != "http":
        return

    path = scope["path"].lstrip("/")
    currency = path.upper() if path else "USD"

    url = f"https://api.exchangerate-api.com/v4/latest/{currency}"

    loop = asyncio.get_event_loop()

    def fetch():
        try:
            with request.urlopen(url, timeout=10) as response:
                return response.read()

        except error.HTTPError as e:
            return json.dumps({"error": f"HTTP Error {e.code}"}).encode()

        except Exception as e:
            return json.dumps({"error": str(e)}).encode()

    body = await loop.run_in_executor(None, fetch)

    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"application/json")],
        }
    )

    await send({"type": "http.response.body", "body": body})
