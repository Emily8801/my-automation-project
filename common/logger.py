import logging
import sys
from datetime import datetime

def get_logger(name = "LoginTest"):
    logger = logging.getLogger(name)
    if logger.handlers:   #避免重复添加handler
        return logger

    logger.setLevel(logging.INFO)

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # 文件输出（按天分割）
    log_file = f"logs/test_{datetime.now().strftime('%y%m%d')}.log"
    file_handler = logging.FileHandler(log_file,encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

