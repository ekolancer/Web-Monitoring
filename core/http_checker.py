import time
import aiohttp
import asyncio

class HTTPChecker:
    def __init__(self, concurrency: int = 25, timeout: int = 10):
        self.sem = asyncio.Semaphore(concurrency)
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> dict:
        async with self.sem:
            start = time.perf_counter()
            try:
                async with session.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True,
                    ssl=False,
                    headers={"User-Agent": "Mozilla/5.0"}
                ) as resp:
                    text = await resp.text()
                    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
                    return {
                        "ok": True,
                        "url": url,
                        "final": str(resp.url),
                        "status": resp.status,
                        "latency": elapsed_ms,
                        "headers": dict(resp.headers),
                        "text": text,
                    }
            except Exception as e:
                return {"ok": False, "url": url, "error": str(e)}
