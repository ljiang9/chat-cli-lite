import unittest

from chat_cli.mock import MockResponder


class TestMockResponder(unittest.TestCase):
    def setUp(self):
        self.mock = MockResponder()

    def test_greeting(self):
        history = [{"role": "user", "content": "你好"}]
        out = self.mock.reply("你好", history)
        self.assertIn("你好", out)

    def test_echo_and_turn_count(self):
        history = [{"role": "user", "content": "第一个问题"}, {"role": "user", "content": "第二个问题"}]
        out = self.mock.reply("今天天气如何", history)
        self.assertIn("今天天气如何", out)
        self.assertIn("2", out)

    def test_question_mark(self):
        out = self.mock.reply("什么是 RAG？", [{"role": "user", "content": "什么是 RAG？"}])
        self.assertIn("无法联网", out)

    def test_short_input(self):
        out = self.mock.reply("好", [])
        self.assertIn("好", out)


if __name__ == "__main__":
    unittest.main()
