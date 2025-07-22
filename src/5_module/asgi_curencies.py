import asyncio
import json
from urllib import error, request

"""
Любая валюта сравнивает свой курс с USD
При выборе USD возвращается стандартный json со списком всех валют
"""


async def app(scope, receive, send):
    if scope["type"] != "http":
        return

    path = scope["path"].lstrip("/")
    currency = path.upper() if path else "USD"

    loop = asyncio.get_event_loop()

    def fetch():
        try:
            if not currency == "USD":
                url = "https://api.exchangerate-api.com/v4/latest/USD"

                with request.urlopen(url, timeout=10) as response:
                    data = json.loads(response.read().decode("UTF-8"))
                    rate = data["rates"][currency]

                    response.result = {
                        "base": "USD",
                        "base_rate": 1,
                        "target": currency,
                        "rate": rate,
                        "provider": "https://www.exchangerate-api.com",
                    }

                    return json.dumps(response.result).encode()

            else:
                url = f"https://api.exchangerate-api.com/v4/latest/{currency}"

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
