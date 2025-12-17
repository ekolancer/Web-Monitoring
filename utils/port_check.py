import socket

COMMON_PORTS = [21, 22, 25, 80, 443, 3306, 6379]

def check_ports(domain: str) -> dict:
    open_ports = []

    for port in COMMON_PORTS:
        try:
            sock = socket.create_connection((domain, port), timeout=1)
            open_ports.append(port)
            sock.close()
        except:
            pass

    if open_ports:
        return {
            "check_type": "Open Ports",
            "status": "WARN",
            "severity": "Medium",
            "detail": f"Open ports detected: {open_ports}"
        }

    return {
        "check_type": "Open Ports",
        "status": "OK",
        "severity": "Low",
        "detail": "No common ports exposed"
    }
