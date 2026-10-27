# 第 1 周：工程基础收尾（知识汇总与复盘）

## 一、 核心代码套路（以后直接抄）

### 1. 虚拟环境与依赖管理 (D6)
- 项目必须独立建 `.venv`，使用 `requirements.txt` 锁定包。
- 敏感信息（如 API Key）一律放 `.env`，禁止硬编码。
- `.gitignore` 必须包含：`.venv/`、`.env`、`weather.log`、`result.json`、`__pycache__/`。
- 提供 `.env.example` 让别人知道需要填什么变量，但不泄露真值。

### 2. 网络请求与重试机制 (D5)
- `timeout=10`：防止服务器不响应导致程序永远卡死。
- 指数退避：`wait = 2 ** i`，失败后等 1s, 2s, 4s。
- `raise_for_status()`：遇到 4xx/5xx 主动抛异常，需配合 `try/except`。
- **必须分类处理异常**：
  - `Timeout/ConnectionError`：网络/服务抽风 → 值得重试。
  - `401/403`：Key 不对 → 重试无用，立刻报错。
  - `400/404`：参数错/城市找不到 → 重试无用，立刻报错。
  - **注意和风天气坑点**：查不到城市时，地理接口返回的是 `400`，不是 `404`。

### 3. 优雅的异常捕获 (D7)
- **必须先判特定状态码，再调 `raise_for_status()`**。否则 400/401 会被统统当成 `HTTPError`。
- 自定义异常类（`CityNotFoundError` 等）继承 `Exception` 即可。
- `except` 的顺序非常重要：**子类异常必须写在 `except Exception` 前面**，否则会被宽泛的兜底全部吃掉，导致无法执行 `sys.exit(2/3/4)`。

### 4. 退出码约定 (D7)
- `0` = 成功
- `1` = 参数错误 / 保存失败
- `2` = 城市不存在 (`CityNotFoundError`)
- `3` = 认证失败 (`WeatherAuthError`)
- `4` = 服务不可用 (`WeatherServiceError`)

---

## 二、 pytest 单元测试与 Mock 原理 (D7)

### 1. pytest 基础
- 测试文件以 `test_` 开头，函数以 `test_` 开头。
- `assert 条件`，成立则绿，不成立则红。
- 项目根目录放一个空的 `conftest.py`，解决跨目录 `import` 找不到模块的痛点（本质是告诉 pytest 将根目录加入环境变量）。

### 2. MagicMock 原理
- `MagicMock()` **不是智能识别类类型**，它是一个“万能假对象”。你访问它的任何属性，它都会当场再变出一个新的假对象给你，绝不报错。
- 所以必须**手动设值**：`fake.status_code = 200`，`fake.json.return_value = {...}`。

### 3. patch 与测试断言
- `patch("client.requests.get")`：因为 `client.py` 里是 `import requests`，所以拦截路径是 `client.requests.get`。
- `side_effect=[fake1, fake2]`：按顺序“发牌”，应对一次业务流里多次调用接口的情况（如先查地理，再查天气）。
- `pytest.raises(异常类)`：断言这里必须抛出指定异常。
- `assert mock_get.call_count == 1`：测试守门员，确保 4xx 错误只请求了 1 次，没有偷偷去重试。

---

## 三、 本周真实踩坑记录（防遗忘）

1. **`==` 与 `in` 的混淆**：
   错写：`if status_code == (400, 404):` （整数永远不等于元组）
   正确：`if status_code in (400, 404):`
2. **文件没保存**：
   报错一直存在，是因为 VS Code 里的文件没按 `Ctrl+S`。以后报错先看标签页有没有小圆点。
3. **缺少 `errors.py`**：
   `client.py` 引用了自定义异常，但忘记新建文件，导致 `ModuleNotFoundError`。
4. **安全警告**：
   调试时明文暴露了真实 API Key，以后任何日志、报错、对话中，**绝对不能出现明文 key**，去平台重置。

---

## 四、 标准复盘（文档要求：3+3+1）

### 3 条以后能复用
1. 工程隔离三板斧：`venv` + `requirements.txt` + `.env`。
2. 异常分类与指数退避机制，是后续调大模型 API（LLM）的通用模板。
3. 用 Mock 和 `call_count` 隔离网络测试，防止测试时乱花 API 钱。

### 3 个踩过的坑
1. `status_code == (400, 404)` 语法错误。
2. `except` 顺序写反，导致被 `Exception` 兜底吃掉。
3. 测试文件找不到模块，没加 `conftest.py`。

### 1 个下周要补
- 第 2 周 D1：给 `client.py` 的方法加类型注解（`-> str`），并确保 pytest 依然绿。