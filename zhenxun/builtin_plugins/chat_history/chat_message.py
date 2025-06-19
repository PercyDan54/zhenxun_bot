from nonebot import on_message
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import UniMsg
from nonebot_plugin_session import EventSession

from zhenxun.configs.config import Config
from zhenxun.configs.utils import PluginExtraData, RegisterConfig
from zhenxun.models.chat_history import ChatHistory
from zhenxun.services.log import logger
from zhenxun.utils.enum import PluginType

from typing import List

__plugin_meta__ = PluginMetadata(
    name="消息存储",
    description="消息存储，被动存储群消息",
    usage="",
    extra=PluginExtraData(
        author="HibiKier",
        version="0.1",
        plugin_type=PluginType.HIDDEN,
        configs=[
            RegisterConfig(
                module="chat_history",
                key="FLAG",
                value=True,
                help="是否开启消息自从存储",
                default_value=True,
                type=bool,
            ),
            RegisterConfig(
                module="chat_history",
                key="BLACK_WORD",
                help="包含以下关键词消息不存储",
                value=["签到", "抽签", "http:", "https:", "pptth", "nbnhhsh", "io"],
                default_value=["签到", "抽签", "http:", "https:", "pptth", "nbnhhsh", "io"],
                type=List[str],
            ),
            RegisterConfig(
                module="chat_history",
                key="BLACKLIST_USER",
                help="以下用户的消息不存储",
                value= [],
                default_value=[],
                type=List[int],
            ),
        ],
    ).to_dict(),
)


def rule(message: UniMsg) -> bool:
    return bool(Config.get_config("chat_history", "FLAG") and message)


chat_history = on_message(rule=rule, priority=1, block=False)


@chat_history.handle()
async def handle_message(message: UniMsg, session: EventSession):
    """处理消息存储"""
    try:
        msg = str(message).strip()
        blacklist_users = Config.get_config("chat_history", "BLACKLIST_USER")
        black_words = Config.get_config("chat_history", "BLACK_WORD")
        if len(msg) > 200 or session.id1 in blacklist_users or msg.startswith('!') or msg.startswith('！') or msg.startswith('/'):
            return
        for w in black_words:
            if str(w) in msg:
                return
        await ChatHistory.create(
            user_id=session.id1,
            group_id=session.id2,
            text=msg,
            plain_text=message.extract_plain_text(),
            bot_id=session.bot_id,
            platform=session.platform,
        )
    except Exception as e:
        logger.warning("存储聊天记录失败", "chat_history", e=e)
