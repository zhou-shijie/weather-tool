import time
import requests
from requests.exceptions import Timeout,RequestException,ConnectionError
from errors import CityNotFoundError, WeatherAuthError, WeatherServiceError
from logger import setup_logger

logger=setup_logger("weather")

class WeatherClient:
    def __init__(self,base_url,timeout=10,max_retry=3):
        self.base_url=base_url.rstrip("/")
        self.timeout=timeout
        self.max_retry=max_retry


    #**城市查询（地理接口）**，拿 location id
    def _get_city_location_id(self,city_name,key):
        geo_url = "https://mf7p45cfey.re.qweatherapi.com/geo/v2/city/lookup"
        response=requests.get(geo_url,timeout=self.timeout,params={"location":city_name,"key":key})

        #先判状态码再 raise_for_status
        if response.status_code in (401,403):
            raise WeatherAuthError(f"认证失败：{response.status_code}")
        if response.status_code in (400,404):
            raise CityNotFoundError(city_name)

        response.raise_for_status()
        res_json=response.json()
        if res_json["code"]== "200":
           if res_json["location"]:
               return res_json["location"][0]["id"]
           
        return None   
               

    def get_weather(self,city_name):
        from config import QWEATHER_KEY
        location_id=self._get_city_location_id(city_name,QWEATHER_KEY)
        if not location_id:
            raise CityNotFoundError(city_name)

        for i in range(self.max_retry):
            try:
                logger.info(f"查询天气:{city_name}")
                response=requests.get(self.base_url,timeout=self.timeout,params={"location":location_id,"key":QWEATHER_KEY})
                response.raise_for_status()
                res_json=response.json()
                if res_json["code"]=="200":
                    logger.info(f"查询成功：{city_name}")
                    now=res_json["now"]
                    weather_str = f"{city_name}: {now['text']}, 温度 {now['temp']}℃, 体感 {now['feelsLike']}℃, 风向 {now['windDir']}"
                    return weather_str
                else:
                    logger.warning(f"第 {i+1} 次请求返回错误码：{res_json['code']}")
            
            except(WeatherAuthError,CityNotFoundError):
                raise   # 这两类不重试，直接往上抛

            except (Timeout,ConnectionError) as e:
                 logger.warning(f"第 {i+1} 次请求失败：{e}")
                 if i==self.max_retry:
                     raise WeatherAuthError("网络错误，重试次数耗尽") from e

            except Exception as e:
                   # 其他错（如 5xx HTTPError）今天先不细分，按服务不可用处理
                logger.warning(f"第 {i+1} 次请求失败：{e}")
                if i == self.max_retry - 1:
                    raise WeatherServiceError(str(e)) from e    

                
            if i < self.max_retry - 1:          # 最后一次失败后不必再等
                wait = 2 ** i                    # 1s, 2s, 4s ...
                logger.info(f"{wait}s 后重试")
                time.sleep(wait)         
        raise WeatherAuthError("天气查询多次重试失败")        
                