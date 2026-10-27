from unittest.mock import MagicMock, patch

import pytest

from client import WeatherClient
from errors import CityNotFoundError
#假地址，不会真发请求。因为 requests.get 被 patch 了，这个 URL 只用来构造 WeatherClient，不参与网络
BASE_URL = "https://fake.example.com/weather"

#辅助函数：造一个假响应
# 抽成 fixture，返回一个“造响应的工厂函数”
@pytest.fixture
def fake_response():
    def _make(status_code,payload):
        fake=MagicMock()
        fake.status_code=status_code
        fake.json.return_value=payload
        return fake
    return _make

#第一条测试：正常返回
#把正常返回的测试改成参数化，传 3 个城市名
@pytest.mark.parametrize("city_name",["成都", "绵阳", "北京"])
def test_normal_return_contains_city_and_temp(fake_response, city_name):
    #这是地理接口的假响应：状态 200，业务码 200，location 里有一个城市 id
    fake_geo = fake_response(
        200,
        {"code": "200", "location": [{"id": "101270101"}]},
    )
    #这是天气接口的假响应
    fake_weather = fake_response(
        200,
        {
            "code": "200",
            "now": {"text": "多云", "temp": "22", "feelsLike": "23", "windDir": "东南风"},
        },
    )
    #把两次请求按顺序换成假响应
    with patch("client.requests.get",side_effect=[fake_geo,fake_weather]):
        client=WeatherClient(base_url=BASE_URL,timeout=1,max_retry=3)
        result=client.get_weather("成都")
    #断言
    assert "成都" in result
    assert "22" in result

#第二条测试：城市不存在，且只请求一次
def test_city_not_found_raises_and_calls_once(fake_response):
    fake_geo = fake_response(400, {"code": "400"})
    with patch("client.requests.get",return_value=fake_geo) as mock_get:
        client=WeatherClient(base_url=BASE_URL, timeout=1, max_retry=3)
        with pytest.raises(CityNotFoundError):
            client.get_weather("火星")

    assert mock_get.call_count == 1        
