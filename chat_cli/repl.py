"""异步交互式命令行（REPL）。

支持斜杠命令：
    /reset  清空对话历史
    /exit   退出
"""

from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

from .client import ChatClient
from .mock import MockResponder

BANNER = (
    "=== chat-cli-lite 终端对话 ==="
    "\n输入内容开始对话；斜杠命令：/reset 清空历史，/exit 退出。"
)


class Repl:
    """多轮对话 REPL。有 key 用真实接口，无 key 自动降级 Mock。"""

    def __init__(self, client: Optional[ChatClient] = None,
                 mock: Optional[MockResponder] = None,
                 stream: bool = False) -> None:
        self.client = client or ChatClient()
        self.mock = mock or MockResponder()
        self.stream = stream
        self.history: List[Dict[str, str]] = []
        self.use_llm = self.client.is_available()

    def mode_line(self) -> str:
        return "已连接真实模型（" + self.client.model + "）" if self.use_llm else "本地 Mock 模式（未检测到 OPENAI_API_KEY）"

    async def handle(self, user_text: str) -> str:
        """处理一条用户输入，返回助手回复文本（供测试调用）。"""
        user_text = user_text.strip()
        self.history.append({"role": "user", "content": user_text})

        if self.use_llm:
            if self.stream:
                chunks: List[str] = []
                await self.client.chat_stream(self.history, chunks.append)
                answer = "".join(chunks)
            else:
                answer = await self.client.chat(self.history)
        else:
            await asyncio.to_thread(lambda: None)  # 让出事件循环，保持异步形态
            answer = self.mock.reply(user_text, self.history)

        self.history.append({"role": "assistant", "content": answer})
        return answer

    def reset(self) -> None:
        self.history.clear()

    async def run(self) -> None:
        print(BANNER)
        print("当前模式：" + self.mode_line())
        while True:
            try:
                user_text = await asyncio.to_thread(input, "你> ")
            except EOFError:
                print()
                break
            user_text = user_text.strip()
            if not user_text:
                continue
            if user_text == "/exit":
                print("再见！")
                break
            if user_text == "/reset":
                self.reset()
                print("（已清空对话历史）")
                continue
            try:
                answer = await self.handle(user_text)
            except Exception as exc:  # 网络错误等不应让 REPL 崩溃
                print(f"[请求失败] {exc}")
                continue
            print("助手> " + answer)
