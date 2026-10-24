import os
from dotenv import load_dotenv
#加载.env的环境变量
load_dotenv()

#**实况天气接口**，拿温度、天气文字
WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://mf7p45cfey.re.qweatherapi.com/v7/weather/now")
QWEATHER_KEY = os.getenv("QWEATHER_KEY")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", 10))
