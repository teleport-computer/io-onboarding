"""Minimal AstrBot API doubles so plugin logic tests run without AstrBot."""
from __future__ import annotations

import sys
import types
from pathlib import Path


PLUGIN_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_DIR))


class _Logger:
    def __getattr__(self, _name):
        return lambda *_args, **_kwargs: None


class AstrBotConfig(dict):
    pass


class Context:
    async def send_message(self, unified_msg_origin, chain):
        raise NotImplementedError


class Star:
    def __init__(self, _context):
        self._kv = {}

    async def get_kv_data(self, key, default=None):
        return self._kv.get(key, default)

    async def put_kv_data(self, key, value):
        self._kv[key] = value

    async def delete_kv_data(self, key):
        self._kv.pop(key, None)


class AstrMessageEvent:
    pass


class MessageChain:
    def __init__(self):
        self.parts = []

    def message(self, text):
        self.parts.append(str(text))
        return self


class EventMessageType:
    PRIVATE_MESSAGE = "private"
    GROUP_MESSAGE = "group"


def _decorator(*_args, **_kwargs):
    return lambda function: function


filter_module = types.ModuleType("astrbot.api.event.filter")
filter_module.EventMessageType = EventMessageType
filter_module.event_message_type = _decorator
filter_module.command = _decorator

astrbot_module = types.ModuleType("astrbot")
api_module = types.ModuleType("astrbot.api")
event_module = types.ModuleType("astrbot.api.event")
star_module = types.ModuleType("astrbot.api.star")

api_module.AstrBotConfig = AstrBotConfig
api_module.logger = _Logger()
event_module.AstrMessageEvent = AstrMessageEvent
event_module.MessageChain = MessageChain
event_module.filter = filter_module
star_module.Context = Context
star_module.Star = Star

sys.modules.setdefault("astrbot", astrbot_module)
sys.modules.setdefault("astrbot.api", api_module)
sys.modules.setdefault("astrbot.api.event", event_module)
sys.modules.setdefault("astrbot.api.event.filter", filter_module)
sys.modules.setdefault("astrbot.api.star", star_module)
