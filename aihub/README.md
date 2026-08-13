# AI 对话模块

## 架构

本模块使用 OpenAI 兼容协议，通过 `AI_BASE_URL` 配置可切换不同的 AI 服务商。

```
前端 (Vue SPA)  →  Django 后端 (aihub/views.py)  →  OpenAI 兼容 API
                      │
                      └── aihub/client.py 封装调用
```

## 配置项

在系统环境变量中设置（`config/settings.py` 第 281-285 行通过 `os.environ.get()` 读取）：

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `AI_API_KEY` | (空) | API 密钥 |
| `AI_BASE_URL` | `https://api.openai.com/v1` | API 地址 |
| `AI_MODEL` | `gpt-4o-mini` | 模型名称 |
| `AI_TIMEOUT` | `60` | 超时秒数 |
| `AI_MAX_RETRIES` | `1` | 超时重试次数 |

## 内网部署方案

服务器无外网时，需要在内网部署一个 OpenAI 兼容的 AI 服务，然后修改 `AI_BASE_URL` 指向它。

### 方案一：Ollama（推荐，零成本）

在内网找一台有 GPU 的机器（或当前服务器，CPU 也能跑小模型），部署 [Ollama](https://ollama.com)。

```
┌──────────────┐      http://内网IP:11434/v1      ┌──────────────────┐
│  Django 后端  │ ──────────────────────────────→ │  Ollama 服务器    │
│  (无外网)     │                                  │  (内网，有GPU)     │
└──────────────┘                                  └──────────────────┘
```

**Ollama 服务器上操作：**

```bash
# 1. 安装 Ollama（Linux）
curl -fsSL https://ollama.com/install.sh | sh

# 2. 下载模型（需要这一次外网，之后完全离线可用）
ollama pull qwen2.5:7b        # 通义千问 7B，中文效果好
# 或
ollama pull deepseek-r1:8b    # DeepSeek 推理模型，适合复杂任务

# 3. 启动服务（默认监听 11434 端口）
ollama serve
```

**Django 项目配置（设置系统环境变量）：**

`settings.py` 通过 `os.environ.get()` 读取环境变量，所以需要设置系统环境变量（Windows 可以在 `启动脚本` 或 `系统环境变量` 中设置）：

```bash
# Windows PowerShell
$env:AI_BASE_URL="http://192.168.x.x:11434/v1"
$env:AI_API_KEY="ollama"
$env:AI_MODEL="qwen2.5:7b"

# Linux
export AI_BASE_URL=http://192.168.x.x:11434/v1
export AI_API_KEY=ollama
export AI_MODEL=qwen2.5:7b
```

> 对应的 `settings.py` 配置项位于 `config/settings.py` 第 281-285 行。

### 方案二：公司内部 AI 平台

如果公司已有内部 AI 平台（如内部部署的通义千问、DeepSeek、文心一言等），只需确认是否提供 OpenAI 兼容接口，然后设置环境变量：

```bash
# Windows
$env:AI_BASE_URL="http://ai-platform.company.com/v1"
$env:AI_API_KEY="公司分配的key"
$env:AI_MODEL="公司模型名"

# Linux
export AI_BASE_URL=http://ai-platform.company.com/v1
export AI_API_KEY=公司分配的key
export AI_MODEL=公司模型名
```

### 方案三：HTTP 代理出网

如果内网允许通过 HTTP 代理访问外网，可设置代理环境变量后使用外部 API：

```bash
# Windows (PowerShell)
$env:HTTP_PROXY="http://proxy.company.com:8080"
$env:HTTPS_PROXY="http://proxy.company.com:8080"

# Linux
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

## 可用性矩阵

| 条件 | 是否可用 |
|---|---|
| 无外网 + 无内部 AI 服务 | 不可用 |
| 无外网 + 部署 Ollama | 完全可用 |
| 无外网 + 公司内部 AI 平台 | 完全可用 |
| 有 HTTP 代理出网 | 可用（需配置代理） |
| 有外网 + 有 API Key | 直接可用 |

## 错误说明

| 错误类型 | 含义 | 解决方向 |
|---|---|---|
| `ConnectTimeout` | TCP 连接超时 | 检查网络 / 代理 / AI_BASE_URL 是否正确 |
| `AuthenticationError` | API Key 无效 | 检查 AI_API_KEY 是否配置 |
| `APIConnectionError` | 无法连接 | 检查 AI_BASE_URL 地址是否可达 |

## 目录结构

```
aihub/
├── __init__.py
├── apps.py           # Django App 配置
├── client.py         # AI 客户端封装（OpenAI 兼容）
├── models.py         # ChatSession / ChatMessage 数据模型
├── views.py          # 对话接口（普通 / 流式 SSE）
├── urls.py           # 路由
├── admin.py          # Django Admin 注册
├── migrations/       # 数据库迁移
└── README.md         # 本文件
```