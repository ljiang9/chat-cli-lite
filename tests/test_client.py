import asyncio
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from chat_cli.client import ChatClient


class _FakeHandler(BaseHTTPRequestHandler):
    # 由测试类在启动服务器前设置，决定返回普通 JSON 还是 SSE 流
    mode = "json"

    def log_message(self, *args):  # 静默
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        payload = json.loads(body.decode("utf-8"))
        assert payload["model"] == "test-model"
        if self.mode == "json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = {"choices": [{"message": {"role": "assistant", "content": "你好，这是真实回复"}}]}
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for tok in ["你", "好", "，流式"]:
                chunk = {"choices": [{"delta": {"content": tok}}]}
                self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode("utf-8"))
                self.wfile.flush()
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()


def _start_server(mode: str) -> ThreadingHTTPServer:
    _FakeHandler.mode = mode
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _FakeHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


class TestChatClient(unittest.TestCase):
    def test_unavailable_without_key(self):
        c = ChatClient(api_key="", base_url="http://x", model="m")
        self.assertFalse(c.is_available())
        with self.assertRaises(RuntimeError):
            asyncio.run(c.chat([{"role": "user", "content": "hi"}]))

    def test_non_stream_against_local_server(self):
        srv = _start_server("json")
        try:
            host, port = srv.server_address
            c = ChatClient(api_key="sk-test", base_url=f"http://{host}:{port}/v1", model="test-model")
            self.assertTrue(c.is_available())
            out = asyncio.run(c.chat([{"role": "user", "content": "hi"}]))
            self.assertEqual(out, "你好，这是真实回复")
        finally:
            srv.shutdown()
            srv.server_close()

    def test_stream_against_local_server(self):
        srv = _start_server("stream")
        try:
            host, port = srv.server_address
            c = ChatClient(api_key="sk-test", base_url=f"http://{host}:{port}/v1", model="test-model")
            tokens = []
            asyncio.run(c.chat_stream([{"role": "user", "content": "hi"}], tokens.append))
            self.assertEqual("".join(tokens), "你好，流式")
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
