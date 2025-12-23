import asyncio

COMMON_PORTS = [21, 22, 25, 80, 443, 3306, 6379]

async def check_ports_async(domain: str) -> dict:
    async def check_port(port):
        try:
            reader, writer = await asyncio.open_connection(domain, port)
            writer.close()
            await writer.wait_closed()
            return port
        except:
            return None

    # Jalankan semua port checks secara concurrent
    tasks = [check_port(port) for port in COMMON_PORTS]
    results = await asyncio.gather(*tasks)

    open_ports = [port for port in results if port is not None]

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

# Keep sync version for backward compatibility
def check_ports(domain: str) -> dict:
    import socket
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
