import requests

SENSITIVE_PATHS = [
    "/.env",
    "/.git/config",
    "/phpinfo.php",
    "/backup.zip"
]

def check_sensitive_files(domain: str) -> dict:
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
