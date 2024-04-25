import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from threading import Timer

BASE_URL_LIVE = "https://api.live.bilibili.com/room/v1/Room/get_info?room_id=22230707"

@plugins.register(name="BilibiliLiveStatus",
                  desc="监控Bilibili直播状态",
                  version="1.0",
                  author="Cool",
                  desire_priority=100)
class BilibiliLiveStatus(Plugin):
    live_status = None

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")
        self.check_live_status()

    def get_help_text(self, **kwargs):
        help_text = f"发送【Bilibili】获取直播状态"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()

        if self.content == "Bilibili":
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()
            if self.live_status == 1:
                reply.type = ReplyType.TEXT
                reply.content = "峰哥直播了！"
            else:
                reply.type = ReplyType.TEXT
                reply.content = "峰哥没有直播"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

    def check_live_status(self):
        url = BASE_URL_LIVE
        try:
            response = requests.get(url=url, timeout=2)
            if response.status_code == 200:
                json_data = response.json()
                logger.info(f"接口返回的数据：{json_data}")
                if json_data.get('code') == 0 and 'data' in json_data and 'live_status' in json_data['data']:
                    self.live_status = json_data['data']['live_status']
                    logger.info(f"主接口获取成功：{self.live_status}")
                else:
                    logger.error(f"主接口返回值异常:{json_data}")
                    raise ValueError('not found')
            else:
                logger.error(f"主接口请求失败:{response.text}")
                raise Exception('request failed')
        except Exception as e:
            logger.error(f"接口异常：{e}")
        logger.error("所有接口都挂了,无法获取")
        Timer(60, self.check_live_status).start()

if __name__ == "__main__":
    bilibili_live_status_plugin = BilibiliLiveStatus()