import aiohttp

DANGEROUS_METHODS = ["PUT", "DELETE"]

async def check_http_methods_async(domain: str) -> dict:
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.options(f"http://{domain}") as r:
                allowed = r.headers.get("Allow", "")

                risky = [m for m in DANGEROUS_METHODS if m in allowed]

                if risky:
                    return {
                        "check_type": "HTTP Methods",
                        "status": "CRITICAL",
                        "severity": "High",
                        "detail": f"Dangerous methods enabled: {', '.join(risky)}"
                    }

                return {
                    "check_type": "HTTP Methods",
                    "status": "OK",
                    "severity": "Low",
                    "detail": f"Allowed methods: {allowed}"
                }

    except Exception as e:
        return {
            "check_type": "HTTP Methods",
            "status": "FAIL",
            "severity": "High",
            "detail": str(e)
        }

# Keep sync version for backward compatibility
def check_http_methods(domain: str) -> dict:
    import requests
    try:
        r = requests.options(f"http://{domain}", timeout=10)
        allowed = r.headers.get("Allow", "")

        risky = [m for m in DANGEROUS_METHODS if m in allowed]

        if risky:
            return {
                "check_type": "HTTP Methods",
                "status": "CRITICAL",
                "severity": "High",
                "detail": f"Dangerous methods enabled: {', '.join(risky)}"
            }

        return {
            "check_type": "HTTP Methods",
            "status": "OK",
            "severity": "Low",
            "detail": f"Allowed methods: {allowed}"
        }

    except Exception as e:
        return {
            "check_type": "HTTP Methods",
            "status": "FAIL",
            "severity": "High",
            "detail": str(e)
        }
