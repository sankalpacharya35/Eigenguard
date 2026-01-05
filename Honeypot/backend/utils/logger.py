import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("honeypot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("honeypot")