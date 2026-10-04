import asyncio
import unittest

from chat_cli.client import ChatClient
from chat_cli.repl import Repl


class TestRepl(unittest.TestCase):
    def _make(self) -> Repl:
        # 无 key -> Mock 模式
        client = ChatClient(api_key="", base_url="http://x", model="m")
        return Repl(client=client)

    def test_mock_multi_turn(self):
        repl = self._make()
        self.assertFalse(repl.use_llm)
        a1 = asyncio.run(repl.handle("你好"))
        self.assertIn("你好", a1)
        a2 = asyncio.run(repl.handle("今天天气如何"))
        # 历史应保留两轮 user
        self.assertEqual(sum(1 for m in repl.history if m["role"] == "user"), 2)
        self.assertIn("今天天气如何", a2)

    def test_reset(self):
        repl = self._make()
        asyncio.run(repl.handle("你好"))
        self.assertTrue(repl.history)
        repl.reset()
        self.assertEqual(repl.history, [])

    def test_mode_line(self):
        repl = self._make()
        self.assertIn("Mock", repl.mode_line())


if __name__ == "__main__":
    unittest.main()
