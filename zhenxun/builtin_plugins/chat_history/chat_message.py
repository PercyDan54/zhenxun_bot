from typing import List

from nonebot import on_message
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import UniMsg
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_session import EventSession

from zhenxun.configs.config import Config
from zhenxun.configs.utils import PluginExtraData, RegisterConfig
from zhenxun.models.chat_history import ChatHistory
from zhenxun.services.log import logger
from zhenxun.utils.enum import PluginType

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
                value=["签到", "抽签", "http:", "https:", "pptth", "nbnhhsh", "io"],
                default_value=["签到", "抽签", "http:", "https:", "pptth", "nbnhhsh", "io"],
                type=List[str],
            ),
            RegisterConfig(
                module="chat_history",
                key="BLACKLIST_USER",
                value= [],
                default_value=[],
                type=List[int],
            ),
        ],
    ).dict(),
)


def rule(message: UniMsg) -> bool:
    return bool(Config.get_config("chat_history", "FLAG") and message)


chat_history = on_message(rule=rule, priority=1, block=False)


TEMP_LIST = []


@chat_history.handle()
async def _(message: UniMsg, session: EventSession):
    # group_id = session.id3 or session.id2
    group_id = session.id2

    msg = str(message).strip()
    blacklist_users = Config.get_config("chat_history", "BLACKLIST_USER")
    black_words = Config.get_config("chat_history", "BLACK_WORD")
    if session.id1 in blacklist_users or msg.startswith('!') or msg.startswith('！') or msg.startswith('/'):
        return
    for w in black_words:
        if str(w) in msg:
            return

    TEMP_LIST.append(
        ChatHistory(
            user_id=session.id1,
            group_id=group_id,
            text=msg,
            plain_text=message.extract_plain_text(),
            bot_id=session.bot_id,
            platform=session.platform,
        )
    )


@scheduler.scheduled_job(
    "interval",
    minutes=1,
)
async def _():
    try:
        message_list = TEMP_LIST.copy()
        TEMP_LIST.clear()
        if message_list:
            await ChatHistory.bulk_create(message_list)
        logger.debug(f"批量添加聊天记录 {len(message_list)} 条", "定时任务")
    except Exception as e:
        logger.error(f"定时批量添加聊天记录", "定时任务", e=e)


# @test.handle()
# async def _(event: MessageEvent):
#     print(await ChatHistory.get_user_msg(event.user_id, "private"))
#     print(await ChatHistory.get_user_msg_count(event.user_id, "private"))
#     print(await ChatHistory.get_user_msg(event.user_id, "group"))
#     print(await ChatHistory.get_user_msg_count(event.user_id, "group"))
#     print(await ChatHistory.get_group_msg(event.group_id))
#     print(await ChatHistory.get_group_msg_count(event.group_id))
