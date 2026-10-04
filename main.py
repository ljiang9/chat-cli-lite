"""命令行入口：python3 main.py [--no-stream]

环境变量：
    OPENAI_API_KEY   设置后接入真实模型；不设置则自动进入本地 Mock 模式。
    OPENAI_BASE_URL  OpenAI 兼容接口地址。
    OPENAI_MODEL     模型名。
"""

from __future__ import annotations

import argparse
import asyncio

from chat_cli.client import ChatClient
from chat_cli.repl import Repl


def main() -> None:
    parser = argparse.ArgumentParser(description="chat-cli-lite：零依赖异步终端对话客户端")
    parser.add_argument("--no-stream", action="store_true", help="关闭 SSE 流式输出（默认尝试流式）")
    args = parser.parse_args()

    client = ChatClient()
    repl = Repl(client=client, stream=not args.no_stream)
    asyncio.run(repl.run())


if __name__ == "__main__":
    main()
