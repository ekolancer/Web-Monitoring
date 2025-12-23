import asyncio
from datetime import datetime
from typing import List, Dict, Callable, Any
from utils.security_headers import check_security_headers_async
from utils.http_methods import check_http_methods_async
from utils.sensitive_files import check_sensitive_files_async
from utils.port_check import check_ports_async
from utils.vulnerability_scanner import check_vulnerabilities, check_ssl_vulnerabilities

async def run_security_check_async(vm_list: List[Dict], progress_callback: Callable[[Any], None] = None) -> List[Dict]:
    """
    Menjalankan seluruh security check untuk setiap VM secara async dengan error handling yang robust
    """
    if not vm_list:
        return []

    results = []
    semaphore = asyncio.Semaphore(10)  # Limit concurrent domains to prevent resource exhaustion

    async def check_domain_with_semaphore(vm: Dict) -> List[Dict]:
        async with semaphore:
            domain = vm.get("domain", "")
            if not domain:
                return []

            try:
                return await run_checks_for_domain(domain)
            except Exception as e:
                # Create error result for failed domain
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return [{
                    "timestamp": timestamp,
                    "domain": domain,
                    "check_type": "Domain Check",
                    "status": "ERROR",
                    "severity": "High",
                    "detail": f"Failed to check domain: {str(e)}"
                }]

    # Create tasks for all domains
    tasks = [check_domain_with_semaphore(vm) for vm in vm_list]

    # Process completed tasks and update progress
    for coro in asyncio.as_completed(tasks):
        try:
            domain_results = await coro
            results.extend(domain_results)
        except Exception as e:
            print(f"Unexpected error in security check: {e}")

        if progress_callback:
            progress_callback(None)

    return results

async def run_checks_for_domain(domain: str) -> List[Dict]:
    """Jalankan semua checks untuk satu domain secara concurrent dengan timeout"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Define all check functions
    check_functions = [
        check_security_headers_async,
        check_http_methods_async,
        check_sensitive_files_async,
        check_ports_async,
        check_vulnerabilities,
        check_ssl_vulnerabilities
    ]

    # Create tasks with individual timeouts
    tasks = []
    for check_func in check_functions:
        task = asyncio.create_task(run_single_check_with_timeout(check_func, domain))
        tasks.append(task)

    # Wait for all checks to complete
    check_results = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    for i, result in enumerate(check_results):
        check_name = check_functions[i].__name__.replace('_async', '').replace('check_', '')

        if isinstance(result, Exception):
            # Handle failed check
            results.append({
                "timestamp": timestamp,
                "domain": domain,
                "check_type": check_name.title(),
                "status": "ERROR",
                "severity": "Medium",
                "detail": f"Check failed: {str(result)}"
            })
        elif isinstance(result, dict):
            # Valid result
            result.update({
                "timestamp": timestamp,
                "domain": domain
            })
            results.append(result)
        else:
            # Unexpected result type
            results.append({
                "timestamp": timestamp,
                "domain": domain,
                "check_type": check_name.title(),
                "status": "UNKNOWN",
                "severity": "Low",
                "detail": f"Unexpected result type: {type(result)}"
            })

    return results

async def run_single_check_with_timeout(check_func: Callable, domain: str, timeout: float = 30.0) -> Dict:
    """Run a single check with timeout"""
    try:
        return await asyncio.wait_for(check_func(domain), timeout=timeout)
    except asyncio.TimeoutError:
        return {
            "check_type": check_func.__name__.replace('_async', '').replace('check_', '').title(),
            "status": "TIMEOUT",
            "severity": "Medium",
            "detail": f"Check timed out after {timeout} seconds"
        }
    except Exception as e:
        return {
            "check_type": check_func.__name__.replace('_async', '').replace('check_', '').title(),
            "status": "ERROR",
            "severity": "High",
            "detail": f"Check failed: {str(e)}"
        }

# Keep sync version for backward compatibility
def run_security_check(vm_list: List[Dict], progress_callback: Callable[[Any], None] = None) -> List[Dict]:
    """Sync wrapper for async security check"""
    try:
        return asyncio.run(run_security_check_async(vm_list, progress_callback))
    except Exception as e:
        print(f"Security check failed: {e}")
        return []
