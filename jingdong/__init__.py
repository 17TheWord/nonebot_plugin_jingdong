from typing import List
from random import choice

from nonebot import on_command, get_bot
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent, PrivateMessageEvent
from .data_source import get_item_search_result_list, get_item_detail

jingdong_search = on_command("jingdong_search", aliases={"jdss", "京东搜索"}, priority=5)
jingdong_item_detail = on_command("jingdong_item_detail", aliases={"jdxq", "京东详情", "京东商品"}, priority=5)

"""
        京东：
                京东搜索 [商品名称]     如：京东搜索 笔记本
                            群聊中返回结果为合并转发消息
                            私聊、频道返回结果为长消息
                京东查询 [商品ID]        如：京东详情 123456789
"""


# 直接附参
@jingdong_search.handle()
async def handle_first_receive(event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    if isinstance(event, PrivateMessageEvent):
        await jingdong_search.finish(message="请在群聊内使用该功能！！！")
    else:
        plain_text = args.extract_plain_text()
        if plain_text:
            matcher.set_arg("item", args)


# 二次确认
@jingdong_search.got("item", prompt="你想搜索什么商品呢？")
async def handle_item(event: MessageEvent, item_name: str = ArgPlainText("item")):
    item_list, list_str = await get_item_search_result_list(item_name)
    if isinstance(event, GroupMessageEvent):
        await send_forward_msg(get_bot(), event, get_bot().self_id, item_list)
    elif isinstance(event, PrivateMessageEvent):
        await jingdong_search.finish(message="请在群聊内使用该功能！！！")
    else:
        await jingdong_search.finish(list_str)


# 直接附参
@jingdong_item_detail.handle()
async def handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        matcher.set_arg("itemid", args)


# 二次确认
@jingdong_item_detail.got("itemid", prompt="你想查询哪个商品的信息呢？")
async def handle_item(item_id: str = ArgPlainText("itemid")):
    await jingdong_item_detail.finish(await get_item_detail(item_id))


async def send_forward_msg(
        bot: Bot,
        event: GroupMessageEvent,
        uin: str,
        msgs: List[str]
):
    def to_json(msg):
        return {"type": "node", "data": {"name": choice(list(bot.config.nickname)), "uin": uin, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    await bot.send_group_forward_msg(group_id=event.group_id, messages=messages)
