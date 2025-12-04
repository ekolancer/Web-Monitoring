from urllib.parse import urlparse

def normalize_url(raw: str):
    """Return tuple (https, http) normalized."""
    u = raw.strip().lower().replace(" ", "").rstrip("/")
    domain = u.replace("http://", "").replace("https://", "")
    return f"https://{domain}", f"http://{domain}"

def get_hostname(final_url: str):
    try:
        return urlparse(final_url).hostname or ""
    except:
        return ""
