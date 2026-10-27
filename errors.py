# 自定义异常类，继承自 Python 内置的 Exception
# 作用：让不同的错误能被分开捕获，而不是混在一个 except Exception 里

class CityNotFoundError(Exception):
    """城市查不到（如参数传了'火星'）-> 属于 4xx 客户端错误，不重试，退出码 2"""
    pass

class WeatherAuthError(Exception):
    """API Key 错误或无权限 -> 属于 401/403，不重试，退出码 3"""
    pass

class WeatherServiceError(Exception):
    """网络超时或服务端挂了 -> 属于网络/5xx 错误，会重试，重试耗尽后退出码 4"""
    pass