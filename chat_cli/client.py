"""OpenAI 兼容接口的异步聊天客户端。

仅使用标准库：urllib 负责 HTTP，asyncio.to_thread 把阻塞调用放进线程池，
从而在不引入 requests / httpx / openai 等第三方包的前提下提供 async 接口。

环境变量：
    OPENAI_API_KEY   API 密钥；未设置时客户端不可用，调用方应降级到 Mock。
    OPENAI_BASE_URL  接口地址，默认 https://api.openai.com/v1
    OPENAI_MODEL     模型名，默认 gpt-4o-mini
"""

from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, List, Optional

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


class ChatClient:
    """与 OpenAI 兼容 /chat/completions 接口对话的客户端。"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or DEFAULT_BASE_URL).strip()
        self.model = model or os.environ.get("OPENAI_MODEL") or DEFAULT_MODEL
        self.timeout = timeout

    def is_available(self) -> bool:
        """是否配置了 API key（可用真实接口）。"""
        return bool(self.api_key)

    # ---- 内部：阻塞式 HTTP，交给 to_thread 执行 -------------------------------

    def _build_request(self, payload: Dict[str, Any]) -> urllib.request.Request:
        url = self.base_url.rstrip("/") + "/chat/completions"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {self.api_key}")
        if payload.get("stream"):
            req.add_header("Accept", "text/event-stream")
        return req

    def _chat_blocking(self, messages: List[Dict[str, str]]) -> str:
        payload = {"model": self.model, "messages": messages, "stream": False}
        req = self._build_request(payload)
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]

    def _stream_blocking(
        self, messages: List[Dict[str, str]], on_token: Callable[[str], None]
    ) -> None:
        payload = {"model": self.model, "messages": messages, "stream": True}
        req = self._build_request(payload)
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            for raw in resp:
                line = raw.decode("utf-8").strip()
                if not line or not line.startswith("data:"):
                    continue
                data = line[len("data:"):].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                except json.JSONDecodeError:
                    continue
                delta = obj["choices"][0].get("delta", {}).get("content")
                if delta:
                    on_token(delta)

    # ---- 对外：async 接口 ----------------------------------------------------

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """非流式：返回完整回复文本。"""
        if not self.is_available():
            raise RuntimeError("缺少 OPENAI_API_KEY，无法调用真实接口")
        return await asyncio.to_thread(self._chat_blocking, messages)

    async def chat_stream(self, messages: List[Dict[str, str]],
                          on_token: Callable[[str], None]) -> None:
        """流式（SSE）：每收到一段增量就回调 on_token。"""
        if not self.is_available():
            raise RuntimeError("缺少 OPENAI_API_KEY，无法调用真实接口")
        await asyncio.to_thread(self._stream_blocking, messages, on_token)
