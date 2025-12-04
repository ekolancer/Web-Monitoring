import ssl
import socket
from datetime import datetime, timezone
import certifi
from cryptography import x509
from cryptography.hazmat.backends import default_backend


def ssl_check_sync(hostname: str):
    """
    Return tuple:
    (ssl_status, ssl_days, tls_version, error_reason)
    """

    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(certifi.where())
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # --- CONNECT SOCKET ---
        try:
            sock = socket.create_connection((hostname, 443), timeout=5)
        except Exception as e:
            return ("NO_HTTPS", None, None, f"CONNECT_FAIL: {type(e).__name__}")

        # --- SSL WRAP ---
        try:
            ssock = context.wrap_socket(sock, server_hostname=hostname)
        except ssl.SSLError as e:
            return ("HANDSHAKE_FAIL", None, None, f"SSLERROR: {e.reason}")
        except Exception as e:
            return ("HANDSHAKE_FAIL", None, None, f"WRAP_FAIL: {type(e).__name__}")

        # --- GET RAW CERTIFICATE (binary DER)
        try:
            raw_cert = ssock.getpeercert(binary_form=True)
            tls_version = ssock.version()
        except Exception as e:
            return ("INVALID_CERT", None, None, f"CERT_FAIL: {type(e).__name__}")

        # --- PARSE X509 CERT ---
        try:
            x509_cert = x509.load_der_x509_certificate(raw_cert, default_backend())
        except Exception as e:
            return ("INVALID_CERT", None, tls_version, f"PARSE_FAIL: {type(e).__name__}")

        # --- USE NEW API: not_valid_after_utc ---
        try:
            expiry_utc = x509_cert.not_valid_after_utc  # No deprecation warning
        except AttributeError:
            # fallback for older cryptography versions
            expiry_naive = x509_cert.not_valid_after
            expiry_utc = expiry_naive.replace(tzinfo=timezone.utc)

        now_utc = datetime.now(timezone.utc)
        days = (expiry_utc - now_utc).days

        # --- STATUS EVALUATION ---
        if days < 0:
            return ("EXPIRED", days, tls_version, "-")
        if days < 7:
            return ("CRITICAL", days, tls_version, "-")
        if days < 30:
            return ("WARNING", days, tls_version, "-")

        return ("VALID", days, tls_version, "-")

    except Exception as e:
        return ("NO_HTTPS", None, None, f"UNKNOWN: {type(e).__name__}")
