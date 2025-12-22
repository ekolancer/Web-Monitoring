import asyncio
from datetime import datetime
from utils.security_headers import check_security_headers_async
from utils.http_methods import check_http_methods_async
from utils.sensitive_files import check_sensitive_files_async
from utils.port_check import check_ports_async

async def run_security_check_async(vm_list, progress_callback=None):
    """
    Menjalankan seluruh security check untuk setiap VM secara async
    """
    results = []

    # Buat tasks untuk semua checks secara concurrent
    tasks = []
    for vm in vm_list:
        domain = vm["domain"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task = asyncio.create_task(run_checks_for_domain(domain, timestamp))
        tasks.append(task)

    # Jalankan tasks dan update progress secara real-time
    for task in asyncio.as_completed(tasks):
        try:
            domain_results = await task
            results.extend(domain_results)
        except Exception as e:
            # Handle failed domain check - create error result
            print(f"Error checking domain: {e}")  # Debug
            # You can add a failed result here if needed
            pass
        if progress_callback:
            progress_callback(None)  # Update progress per domain completed

    return results

async def run_checks_for_domain(domain, timestamp):
    """Jalankan semua checks untuk satu domain secara concurrent"""
    checks = await asyncio.gather(
        check_security_headers_async(domain),
        check_http_methods_async(domain),
        check_sensitive_files_async(domain),
        check_ports_async(domain)
    )

    results = []
    for check in checks:
        results.append({
            "timestamp": timestamp,
            "domain": domain,
            "check_type": check["check_type"],
            "status": check["status"],
            "severity": check["severity"],
            "detail": check["detail"]
        })

    return results

# Keep sync version for backward compatibility
def run_security_check(vm_list, progress_callback=None):
    return asyncio.run(run_security_check_async(vm_list, progress_callback))
