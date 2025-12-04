# core/engine.py

import asyncio
import aiohttp
import functools
from typing import List, Dict

from core.http_checker import HTTPChecker
from core.ssl_checker import ssl_check_sync
from utils.normalize import normalize_url, get_hostname
from config import TIMEOUT_MS, SSL_WARNING_DAYS, CONCURRENCY
from datetime import datetime


class MonitorEngine:
    def __init__(self, urls: List[str], concurrency: int = CONCURRENCY):
        self.urls = urls
        self.http = HTTPChecker(concurrency=concurrency)

    async def _ssl_check(self, hostname: str):
        """
        Jalankan ssl_check_sync di thread terpisah supaya non-blocking
        """
        return await asyncio.to_thread(functools.partial(ssl_check_sync, hostname))

    async def scan_one(self, session, raw_url: str) -> Dict:
        https, http = normalize_url(raw_url)

        # --- Try HTTPS lalu HTTP ---
        res = None
        target = None
        for target in (https, http):
            res = await self.http.fetch(session, target)
            if res["ok"]:
                break

        # Jika semua gagal -> UNREACHABLE
        if not res or not res.get("ok"):
            return {
                "Timestamp": datetime_now(),
                "URL": raw_url,
                "Status": "UNREACHABLE",
                "HTTP": None,
                "Latency": None,
                "SSL Status": "NO_HTTPS",
                "SSL Days": None,
                "TLS Version": None,
                "SSL Error": "NO_RESPONSE",
                "Protocol": "-",
                "Server": "-",
                "Cache": "-",
                "CDN": "-",
                "Content": "-",
                "Alerts": "UNREACHABLE",
            }

        final_url = res["final"]
        proto = "HTTPS" if final_url.startswith("https://") else "HTTP"
        hostname = get_hostname(final_url) or get_hostname(target) # pyright: ignore[reportArgumentType]

        # --- SSL check with detailed error ---
        if proto == "HTTPS" and hostname:
            ssl_status, ssl_days, tls, ssl_error = await self._ssl_check(hostname)
        elif proto == "HTTPS":
            ssl_status, ssl_days, tls, ssl_error = (
                "INVALID_CERT",
                None,
                None,
                "NO_HOSTNAME",
            )
        else:
            ssl_status, ssl_days, tls, ssl_error = (
                "NO_HTTPS",
                None,
                None,
                "NOT_USING_HTTPS",
            )

        text_lower = (res.get("text") or "").lower()
        content_ok = any(
            k in text_lower for k in ["bnpb", "login", "portal", "api", "dashboard"]
        )

        # --- Determine status ---
        status = "UNKNOWN"
        http_code = res.get("status")
        latency = res.get("latency")

        if (
            http_code == 200
            and latency is not None
            and latency <= TIMEOUT_MS
            and content_ok
        ):
            status = "HEALTHY"
        elif latency and latency > TIMEOUT_MS:
            status = "SLOW"
        elif http_code == 200 and not content_ok:
            status = "PARTIAL"
        elif http_code and http_code >= 500:
            status = "SERVER ERROR"
        elif http_code and http_code >= 400:
            status = "CLIENT ERROR"

        # --- Alerts ---
        alerts = []

        # SSL warning by days
        if ssl_days is not None and ssl_days <= SSL_WARNING_DAYS:
            alerts.append("SSL WARNING")

        # SSL error type
        if ssl_status in ("INVALID_CERT", "HANDSHAKE_FAIL"):
            alerts.append("SSL ERROR")

        if status in ("UNREACHABLE", "SERVER ERROR", "CLIENT ERROR"):
            alerts.append("STATUS ISSUE")

        if latency and latency > TIMEOUT_MS:
            alerts.append("SLOW RESPONSE")

        return {
            "Timestamp": datetime_now(),
            "URL": raw_url,
            "Status": status,
            "HTTP": http_code,
            "Latency": latency,
            "SSL Status": ssl_status,
            "SSL Days": ssl_days,
            "TLS Version": tls,
            "SSL Error": ssl_error,
            "Protocol": proto,
            "Server": res["headers"].get("Server", "-"),
            "Cache": res["headers"].get("Cache-Control", "-"),
            "CDN": "-",
            "Content": "OK" if content_ok else "NO MATCH",
            "Alerts": ", ".join(alerts) if alerts else "-",
        }

    async def run(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.scan_one(session, url) for url in self.urls]
            return await asyncio.gather(*tasks)


def datetime_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
