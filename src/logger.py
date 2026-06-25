import sys
import os
from loguru import logger

# Make sure logs directory exists
os.makedirs("logs", exist_ok=True)

# Remove default logger
logger.remove()

# Configure custom level names and formatting
# By default, loguru maps colors to levels (INFO -> cyan, SUCCESS -> green, WARNING -> yellow, ERROR -> red)
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<level>{message}</level>"
)

# Add console logger with colored output
logger.add(
    sys.stdout,
    format=log_format,
    colorize=True,
    level="INFO"
)

# Add file logger for persistent execution logs (NFR2)
logger.add(
    "logs/harvester.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="5 MB",
    retention="7 days",
    level="DEBUG"
)

# Helper to log with specific tags for ECI compatibility
def log_success(msg):
    logger.success(f"[SUCCESS] {msg}")

def log_warn(msg):
    logger.warning(f"[WARN] {msg}")

def log_error(msg):
    logger.error(f"[ERROR] {msg}")

def log_info(msg):
    logger.info(f"[INFO] {msg}")
