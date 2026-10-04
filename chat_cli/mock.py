"""无 API key 时的本地 Mock 应答器。

它不访问网络，仅根据用户输入与对话历史生成一个稳定、可读的多轮回复，
让你在没有密钥的情况下也能完整体验多轮对话流程。
"""

from __future__ import annotations

from typing import Dict, List


class MockResponder:
    """内置的规则式本地应答器。"""

    def reply(self, user_text: str, history: List[Dict[str, str]]) -> str:
        turns = sum(1 for m in history if m.get("role") == "user")
        text = user_text.strip()

        lowered = text.lower()
        if any(k in lowered for k in ("你好", "hello", "hi", "在吗")):
            return f"你好呀！我是本地 Mock 助手（第 {turns} 轮对话）。我们可以随便聊聊，输入 /reset 清空历史，/exit 退出。"
        if "你是谁" in text or "你的名字" in text:
            return "我是 chat-cli-lite 的内置 Mock 应答器，没有联网，回答都是本地规则生成的。"
        if "谢谢" in text or "thank" in lowered:
            return "不客气！这是 Mock 模式下的固定回复，有问题继续问就好。"
        if text.endswith("?") or text.endswith("？"):
            return f"（本地模式）关于「{text}」，我无法联网查证，但我记得这是我们第 {turns} 轮对话。配置 OPENAI_API_KEY 后即可获得真实回答。"
        if len(text) <= 2:
            return f"你只说了「{text}」，再多告诉我一点吧～（当前第 {turns} 轮）"
        return f"（Mock 回复）收到你的消息：「{text}」。这是第 {turns} 轮对话，历史已保留；配置 OPENAI_API_KEY / OPENAI_BASE_URL 即可接入真实模型。"
