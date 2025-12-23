import aiohttp
import asyncio

SENSITIVE_PATHS = [
    "/.env",
    "/.git/config",
    "/phpinfo.php",
    "/backup.zip"
]

async def check_sensitive_files_async(domain: str) -> dict:
    async def check_path(path):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"http://{domain}{path}") as r:
                    return path if r.status == 200 else None
        except:
            return None

    # Jalankan semua checks secara concurrent
    tasks = [check_path(path) for path in SENSITIVE_PATHS]
    results = await asyncio.gather(*tasks)

    exposed = [path for path in results if path is not None]

    if exposed:
        return {
            "check_type": "Sensitive Files",
            "status": "CRITICAL",
            "severity": "Critical",
            "detail": f"Exposed files: {', '.join(exposed)}"
        }

    return {
        "check_type": "Sensitive Files",
        "status": "OK",
        "severity": "Low",
        "detail": "No sensitive files exposed"
    }

# Keep sync version for backward compatibility
def check_sensitive_files(domain: str) -> dict:
    import requests
    exposed = []

    for path in SENSITIVE_PATHS:
        try:
            r = requests.get(f"http://{domain}{path}", timeout=5)
            if r.status_code == 200:
                exposed.append(path)
        except:
            pass

    if exposed:
        return {
            "check_type": "Sensitive Files",
            "status": "CRITICAL",
            "severity": "Critical",
            "detail": f"Exposed files: {', '.join(exposed)}"
        }

    return {
        "check_type": "Sensitive Files",
        "status": "OK",
        "severity": "Low",
        "detail": "No sensitive files exposed"
    }
