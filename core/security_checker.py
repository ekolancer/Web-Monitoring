from datetime import datetime
from utils.security_headers import check_security_headers
from utils.http_methods import check_http_methods
from utils.sensitive_files import check_sensitive_files
from utils.port_check import check_ports

def run_security_check(vm_list, progress_callback=None):
    ...

    """
    Menjalankan seluruh security check untuk setiap VM
    """
    results = []

    for vm in vm_list:
        domain = vm["domain"]
        #vm_name = vm["vm_name"]

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        checks = [
            check_security_headers(domain),
            check_http_methods(domain),
            check_sensitive_files(domain),
            check_ports(domain)
        ]

        for check in checks:
            results.append({
                "timestamp": timestamp,
                #"vm_name": vm_name,
                "domain": domain,
                "check_type": check["check_type"],
                "status": check["status"],
                "severity": check["severity"],
                "detail": check["detail"]
            })

    return results
