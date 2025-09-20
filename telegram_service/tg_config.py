import logging
import os

logging.basicConfig(
    filename="logs.log",
    level=logging.WARNING,
    format="""[%(asctime)s] {%(filename)s:%(lineno)d} 
                        %(levelname)s - %(message)s""",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


URL_START = os.environ.get("URL_START")
