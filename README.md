# chat-cli-lite

一个**零第三方依赖**的异步终端多轮对话客户端。使用 Python 标准库 `asyncio` + `urllib` 接入 OpenAI 兼容接口，支持可选的 SSE 流式输出；未配置 API Key 时自动降级到内置 Mock 模式，本地即可体验完整多轮对话。

## 功能特性

- **异步客户端**：`asyncio` + `urllib`（阻塞调用经 `asyncio.to_thread` 调度），无 `requests`/`httpx`/`openai` 依赖。
- **OpenAI 兼容**：读取环境变量 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL`，请求 `/chat/completions`。
- **流式输出（SSE）**：可选 `stream=true`，逐段解析 `data:` 增量。
- **多轮对话**：自动维护 messages 历史。
- **斜杠命令**：`/reset` 清空历史、`/exit` 退出。
- **无 Key 降级**：未检测到 Key 时进入本地 Mock 模式，仍可多轮对话。

## 快速开始

环境要求：Python 3.10+（开发于 3.12）。无需安装任何依赖。

```bash
# 克隆后进入目录
cd chat-cli-lite

# 直接运行（无 Key -> 自动进入本地 Mock 模式）
python3 main.py
```

### 接入真实模型（可选）

```bash
export OPENAI_API_KEY="sk-xxxx"
export OPENAI_BASE_URL="https://api.openai.com/v1"   # 可换成任意 OpenAI 兼容地址
export OPENAI_MODEL="gpt-4o-mini"                    # 可选，默认 gpt-4o-mini
python3 main.py
```

关闭流式输出：

```bash
python3 main.py --no-stream
```

## 使用示例

无 Key 时的实际运行效果：

```
$ python3 main.py
=== chat-cli-lite 终端对话 ===
输入内容开始对话；斜杠命令：/reset 清空历史，/exit 退出。
当前模式：本地 Mock 模式（未检测到 OPENAI_API_KEY）
你> 你好
助手> 你好呀！我是本地 Mock 助手（第 1 轮对话）。我们可以随便聊聊，输入 /reset 清空历史，/exit 退出。
你> 今天天气如何？
助手> （本地模式）关于「今天天气如何？」，我无法联网查证，但我记得这是我们第 2 轮对话。配置 OPENAI_API_KEY 后即可获得真实回答。
你> /reset
（已清空对话历史）
你> /exit
再见！
```

## 无 API Key 如何运行？

直接 `python3 main.py` 即可。程序启动时检测不到 `OPENAI_API_KEY`，会打印「本地 Mock 模式」并使用内置规则应答器回答，多轮历史、`/reset`、`/exit` 全部可用，无需联网。

## 运行测试

在仓库根目录执行（标准库 unittest，不依赖 pytest）：

```bash
python3 -m unittest discover -s tests
```

## 目录结构

```
chat-cli-lite/
├── main.py               # 命令行入口
├── chat_cli/
│   ├── __init__.py
│   ├── client.py         # OpenAI 兼容异步客户端（urllib + asyncio）
│   ├── mock.py           # 无 Key 时的本地 Mock 应答器
│   └── repl.py           # 异步 REPL + 斜杠命令
├── tests/
│   ├── test_client.py    # 本地起 HTTP 服务器验证非流式/流式解析
│   ├── test_mock.py
│   └── test_repl.py
├── README.md
├── LICENSE               # MIT
└── .gitignore
```

## 许可证

[MIT](./LICENSE) © ljiang9
