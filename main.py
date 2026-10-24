import json
import sys
from pathlib import Path

from config import WEATHER_API_URL, API_TIMEOUT
from client import WeatherClient
from logger import setup_logger

logger = setup_logger("weather")


def save_result(city, weather_text):
    """把查询结果保存到 result.json，成功返回 True"""
    data = {"city": city, "weather": weather_text}
    result_path = Path(__file__).resolve().parent / "result.json"
    try:
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"结果已保存到: {result_path}")
        return True
    except OSError as e:
        logger.error(f"保存结果失败: {e}")
        return False


if __name__ == "__main__":

    import argparse
    #创建命令行参数解析器
    parser=argparse.ArgumentParser(description="天气查询")
    #给解释器添加位置参数
    parser.add_argument("city",nargs="?",help="城市名，缺省则交互输入")
    #解析参数
    args=parser.parse_args()

    client = WeatherClient(base_url=WEATHER_API_URL, timeout=API_TIMEOUT)
    city = (args.city or input("请输入城市名（中英文均可，如 Chengdu / 绵阳）：")).strip()

    if not city:
        logger.error("城市名不能为空!")
        sys.exit(1)

    try:
        weather_result = client.get_weather(city)
        print(weather_result)
        if not save_result(city, weather_result):
            sys.exit(1)
    except RuntimeError as e:
        logger.error(e)
        sys.exit(1)
    except Exception as e:
        logger.exception(f"未预期的错误: {e}")
        sys.exit(1)