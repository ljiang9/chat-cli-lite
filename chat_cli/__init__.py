"""chat-cli-lite：零第三方依赖的异步终端多轮对话客户端。"""

from .client import ChatClient
from .mock import MockResponder

__all__ = ["ChatClient", "MockResponder"]
__version__ = "0.1.0"
