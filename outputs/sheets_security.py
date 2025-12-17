def write_security_results(sheet, results: list):
    """
    Menulis hasil Security Check ke sheet 'Security Check'
    """
    rows = [
        [
            r["timestamp"],
            r["vm_name"],
            r["domain"],
            r["check_type"],
            r["status"],
            r["severity"],
            r["detail"]
        ]
        for r in results
    ]

    sheet.append_rows(
        rows,
        value_input_option="USER_ENTERED"
    )
