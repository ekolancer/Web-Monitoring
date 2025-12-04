import os, json
from datetime import datetime
from config import OUTPUT_DIR
from utils.logger import setup_logger

logger = setup_logger()

def write_local_log(results: list) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = datetime.now().strftime(f"{OUTPUT_DIR}/scan_%Y%m%d_%H%M.json")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Local log saved: {filename}")
    except Exception as e:
        logger.error(f"Failed write local log: {e}")
    return filename
