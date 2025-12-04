from rich.table import Table
from rich import box
from rich.text import Text

# --- Table View ---
def make_table(results: list):
    t = Table(box=box.ROUNDED, title="Engine Scan Results", expand=True)
    t.add_column("Website", style="bold cyan")
    t.add_column("Status")
    t.add_column("Latency", justify="right")
    t.add_column("SSL", justify="left")
    t.add_column("Protocol", justify="center")
    t.add_column("Checked", justify="center")

    for r in results:
        url = r.get("URL")
        status = (r.get("Status") or "UNKNOWN").upper()
        latency = f"{r.get('Latency')} ms" if r.get("Latency") is not None else "-"
        ssl = r.get("SSL Status")
        protocol = r.get("Protocol")
        checked = r.get("Timestamp")

        # color/emoji
        if "HEALTHY" in status:
            status_cell = Text(f"🟢 {status}", style="bold green")
        elif "SLOW" in status or "PARTIAL" in status:
            status_cell = Text(f"🟡 {status}", style="bold yellow")
        else:
            status_cell = Text(f"🔴 {status}", style="bold red")

        if r.get("Latency") is None:
            latency_cell = Text(latency, style="white")
        elif r.get("Latency") > 1500:
            latency_cell = Text(latency + " ⚠", style="bold red")
        elif r.get("Latency") > 800:
            latency_cell = Text(latency + " ⚠", style="yellow")
        else:
            latency_cell = Text(latency, style="green")

        if "VALID" in str(ssl).upper():
            ssl_cell = Text(f"🔐 {ssl}", style="green")
        elif "NO HTTPS" in str(ssl).upper():
            ssl_cell = Text(f"⚠ {ssl}", style="yellow")
        else:
            ssl_cell = Text(f"❌ {ssl}", style="red")

        t.add_row(url, status_cell, latency_cell, ssl_cell, protocol, checked)

    return t


# --- Talbe Sorting & Display ---
def make_table_live(results: list):
    from rich.table import Table
    from rich import box
    from rich.text import Text

    # ---- PRIORITY ORDER ----
    STATUS_ORDER = {
        "HEALTHY": 1,
        "SLOW": 2,
        "PARTIAL": 2,
        "UNREACHABLE": 3,
        "SERVER ERROR": 3,
        "CLIENT ERROR": 3,
        "UNKNOWN": 3,
    }

    def status_rank(r):
        """Return numeric order for sorting."""
        s = (r.get("Status") or "UNKNOWN").upper()
        return STATUS_ORDER.get(s, 99)

    # ---- SORTED RESULTS ----
    sorted_results = sorted(results, key=status_rank)

    # ---- TABLE ----
    t = Table(box=box.ROUNDED, title="Engine Scan Results", expand=True)
    t.add_column("Website", style="bold cyan")
    t.add_column("Status")
    t.add_column("Latency", justify="right")
    t.add_column("SSL", justify="left")
    t.add_column("Protocol", justify="center")
    t.add_column("Checked", justify="center")

    for r in sorted_results:
        url = r.get("URL")
        status = (r.get("Status") or "UNKNOWN").upper()
        latency = f"{r.get('Latency')} ms" if r.get("Latency") is not None else "-"
        ssl = r.get("SSL Status")
        protocol = r.get("Protocol")
        checked = r.get("Timestamp")

        # --- STATUS COLORING ---
        if status == "HEALTHY":
            status_cell = Text(f"🟢 {status}", style="bold green")
        elif status in ("SLOW", "PARTIAL"):
            status_cell = Text(f"🟡 {status}", style="bold yellow")
        else:
            status_cell = Text(f"🔴 {status}", style="bold red")

        # --- LATENCY COLORING ---
        if r.get("Latency") is None:
            latency_cell = Text(latency, style="white")
        elif r.get("Latency") > 1500:
            latency_cell = Text(latency + " ⚠", style="bold red")
        elif r.get("Latency") > 800:
            latency_cell = Text(latency + " ⚠", style="yellow")
        else:
            latency_cell = Text(latency, style="green")

        # --- SSL COLORING ---
        ssl_upper = str(ssl).upper()
        if "VALID" in ssl_upper:
            ssl_cell = Text(f"🔐 {ssl}", style="green")
        elif "NO HTTPS" in ssl_upper:
            ssl_cell = Text(f"⚠ {ssl}", style="yellow")
        else:
            ssl_cell = Text(f"❌ {ssl}", style="red")

        t.add_row(url, status_cell, latency_cell, ssl_cell, protocol, checked)

    return t
