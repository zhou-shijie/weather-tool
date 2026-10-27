import logging
from pathlib import Path


# 1. 用一个全局变量存当前的 rid，默认给个 "init"
_CURRENT_ID="init"

# 2. 提供给 main.py 调用的接口，用来修改这个全局变量
def set_request_id(rid):
    global _CURRENT_ID
    _CURRENT_ID=rid

# 3. 定义一个过滤器，它会自动把当前的 rid 塞进每一条日志里
class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.rid=_CURRENT_ID
        return True



def setup_logger(name="weather"):
    logger = logging.getLogger(name)

    # 防止重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | [%(rid)s] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 实例化过滤器
    rid_filter = RequestIDFilter()

    # 终端输出
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(rid_filter)# 挂载过滤器
    logger.addHandler(stream_handler)

    # 文件输出
    log_path = Path(__file__).resolve().parent / "weather.log"
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(rid_filter)   # 挂载过滤器
    logger.addHandler(file_handler)

    return logger