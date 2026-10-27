```markdown
# 天气查询工具（Weather Tool）

基于和风天气 API 的命令行天气查询工具。支持带参数运行、网络重试、错误分类与日志记录。

## 1. 安装依赖

需要 Python 3.9+。在项目根目录执行：

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

## 2. 配置 `.env`

本项目通过环境变量读取 API Key。

```bash
# 复制模板文件
cp .env.example .env   # Windows 可用 copy .env.example .env
```

打开 `.env`，填入你自己的和风天气 Key：

```env
QWEATHER_KEY=你的真实Key
```
> 注意：`.env` 已加入 `.gitignore`，不会被提交到 Git。

## 3. 怎么用

在项目根目录执行：

```bash
# 方式一：直接传城市名
python main.py 成都

# 方式二：交互式输入
python main.py
```

运行成功会打印天气信息，并把结果保存到 `result.json`，日志记录在 `weather.log`。

## 4. 退出码含义

程序出错时会返回不同的退出码，方便脚本调用时判断：

| 退出码 | 含义 |
| :--- | :--- |
| `0` | 成功 |
| `1` | 参数错误、城市名为空或保存结果失败 |
| `2` | 城市不存在（4xx） |
| `3` | 认证失败，Key 无效或无权限（401/403） |
| `4` | 服务不可用，网络错误且重试耗尽（5xx/超时） |

## 5. 错误分类与重试策略

程序对不同的错误做了分类处理，不是所有错误都值得重试：

- **网络超时 / 连接错误** → 进重试（指数退避：1s, 2s, 4s...），最终抛 `WeatherServiceError`（退出码 `4`）。
- **401/403 认证错误** → 不重试，直接抛 `WeatherAuthError`（退出码 `3`）。
- **400/404 城市不存在** → 不重试，直接抛 `CityNotFoundError`（退出码 `2`）。

## 6. 怎么跑测试

本项目使用 `pytest` 编写了冒烟测试，覆盖了正常返回和城市不存在两种情况。

在项目根目录执行：

```bash
pytest -q
```

预期结果：`2 passed`。
## 7. HTTP 状态码与错误分类说明

程序会根据不同的 HTTP 状态码采取不同的重试策略：

| 状态码 | 含义 | 谁的错 | 是否重试 | 对应异常/退出码 |
| :--- | :--- | :--- | :--- | :--- |
| **400 / 404** | 城市查不到 / 参数错误 | 客户端 | 否 | `CityNotFoundError` (退出码 2) |
| **401 / 403** | API Key 错误 / 无权限 | 客户端 | 否 | `WeatherAuthError` (退出码 3) |
| **429** | 请求太频繁（限流） | 客户端 | 是（退避重试） | 当前项目暂未触发 |
| **500 / 503** | 服务器内部错误 / 宕机 | 服务端 | 是（退避重试） | `WeatherServiceError` (退出码 4) |
| **Timeout** | 网络超时 / 连不上 | 网络 | 是（退避重试） | `WeatherServiceError` (退出码 4) |

> **核心理念**：4xx 客户端错误重试无用，直接报错；5xx 服务端错误或网络超时值得重试。