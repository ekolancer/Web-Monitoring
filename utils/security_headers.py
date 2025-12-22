import aiohttp

SECURITY_HEADERS = [
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Content-Security-Policy"
]

async def check_security_headers_async(domain: str) -> dict:
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(f"http://{domain}") as r:
                missing = [h for h in SECURITY_HEADERS if h not in r.headers]

                if missing:
                    return {
                        "check_type": "Security Headers",
                        "status": "WARN",
                        "severity": "Medium",
                        "detail": f"Missing headers: {', '.join(missing)}"
                    }

                return {
                    "check_type": "Security Headers",
                    "status": "OK",
                    "severity": "Low",
                    "detail": "All recommended headers present"
                }

    except Exception as e:
        return {
            "check_type": "Security Headers",
            "status": "FAIL",
            "severity": "High",
            "detail": str(e)
        }

# Keep sync version for backward compatibility
def check_security_headers(domain: str) -> dict:
    import requests
    try:
        r = requests.get(f"http://{domain}", timeout=10)
        missing = [h for h in SECURITY_HEADERS if h not in r.headers]

        if missing:
            return {
                "check_type": "Security Headers",
                "status": "WARN",
                "severity": "Medium",
                "detail": f"Missing headers: {', '.join(missing)}"
            }

        return {
            "check_type": "Security Headers",
            "status": "OK",
            "severity": "Low",
            "detail": "All recommended headers present"
        }

    except Exception as e:
        return {
            "check_type": "Security Headers",
            "status": "FAIL",
            "severity": "High",
            "detail": str(e)
        }
