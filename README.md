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