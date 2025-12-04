import ssl
import socket
from datetime import datetime, timezone
import certifi
import re


def clean_hostname(hostname: str):
    """Extract pure hostname without schema/path/port."""
    hostname = hostname.lower()

    # remove http, https
    hostname = re.sub(r"^https?://", "", hostname)

    # remove path
    hostname = hostname.split("/")[0]

    # remove port
    hostname = hostname.split(":")[0]

    return hostname.strip()


def ssl_check_sync(hostname: str):
    """
    Return:
    (ssl_status, ssl_days, tls_version, error_reason)
    """

    hostname = clean_hostname(hostname)

    try:
        # --- PREP TLS CONTEXT ---
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

        # Force TLS 1.2–1.3 only
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1

        # Load CA bundle
        context.load_verify_locations(certifi.where())

        # ALPN negotiation
        try:
            context.set_alpn_protocols(["http/1.1"])
        except Exception:
            pass  # older python

        # allow invalid certs but still read them
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # --- CONNECT SOCKET ---
        try:
            sock = socket.create_connection((hostname, 443), timeout=5)
        except Exception as e:
            return ("NO_HTTPS", None, None, f"CONNECT_FAIL:{type(e).__name__}")

        # --- SSL HANDSHAKE ---
        try:
            ssock = context.wrap_socket(sock, server_hostname=hostname)
        except ssl.SSLError as e:
            return ("HANDSHAKE_FAIL", None, None, f"SSL:{e.reason}")
        except Exception as e:
            return ("HANDSHAKE_FAIL", None, None, f"WRAP:{type(e).__name__}")

        # --- RETRIEVE CERT ---
        try:
            cert = ssock.getpeercert()
            tls_version = ssock.version()
        except Exception as e:
            return ("INVALID_CERT", None, None, f"CERT_READ:{type(e).__name__}")

        if not cert or "notAfter" not in cert:
            return ("INVALID_CERT", None, tls_version, "NO_NOTAFTER")

        # --- EXPIRY CALC ---
        try:
            expiry = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
            now = datetime.now(timezone.utc)
            expiry_utc = expiry.replace(tzinfo=timezone.utc)
            days = (expiry_utc - now).days
        except Exception:
            return ("INVALID_CERT", None, tls_version, "PARSE_FAIL")

        # ---- STATUS -----
        if days < 0:
            return ("EXPIRED", days, tls_version, "-")
        if days < 7:
            return ("CRITICAL", days, tls_version, "-")
        if days < 30:
            return ("WARNING", days, tls_version, "-")

        return ("VALID", days, tls_version, "-")

    except Exception as e:
        return ("NO_HTTPS", None, None, f"UNKNOWN:{type(e).__name__}")
