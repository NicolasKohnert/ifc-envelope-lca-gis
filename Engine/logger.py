import logging
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent

def setup_logger():
    log_dir = BASE_PATH / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("BIM-GIS_Pipeline")

logger = setup_logger()

if __name__ == "__main__":
    logger = setup_logger()
    logging.info("Test-Log: Successfully set up the logger.")
