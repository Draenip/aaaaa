from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
from pkg.platform.types import *
from pkg.core.entities import LauncherTypes
from plugins.JM_PDF_plugin.utils.image2pdf import *
from plugins.JM_PDF_plugin.utils.sendfile import *
import re
import os

current_dir = os.path.dirname(__file__)

# 注册插件
@register(name="JMcomicPDF", description="迅速突破卡脖子核心技术", version="1.0", author="Amethyst")
class JMcomicPDFPlugin(BasePlugin):
    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.send_file = send_file(host="127.0.0.1", port=3000)
        self.pdf_dir = os.path.join(current_dir, "downloads")
        self.instructions = {
            "/jm": r"^/jm$",
            "/jm [ID]": r"^/jm (\d+)$",
            "/jm [ID] [CHAPTER]": r"^/jm (\d+) (\d+)$"
        }
    
    def matchPattern(self, msg):
        '''
        匹配指令
        
        args:
            msg: 指令内容
        return:
            匹配结果
        '''
        res = None
        for pattern in self.instructions:
            if re.match(self.instructions[pattern], msg):
                res = pattern
        return res
    
    # 异步初始化
    async def initialize(self):
        pass

    # 当收到群/私聊消息时触发
    @handler(PersonMessageReceived)
    @handler(GroupMessageReceived)
    async def group_message_received(self, ctx: EventContext):
        msg = str(ctx.event.message_chain).strip()
        # 匹配指令
        match self.matchPattern(msg):
            case "/jm":
                await ctx.reply(MessageChain([
                    Plain("jm卡脖子核心技术\n"),
                    Plain("将jm号对应本子转化为pdf，请输入jm号进行转化，如：/jm 123456")
                ]))
            case "/jm [ID]":
                manga_id = re.search(r"^/jm (\d+)$", msg).group(1)
                await ctx.reply(MessageChain([
                    Plain(f"正在将jm{manga_id}转换为PDF...\n可能需要10s至1min不等，请耐心等待")
                ]))
                chap = ""
                if not mangaCache(manga_id):
                    downloadManga(manga_id)
                if convertPDF([manga_id]) == 1:
                    await ctx.reply(MessageChain([
                        Plain(f"检测到jm{manga_id}存在多个章节，现在默认转换第一话\n请输入“/jm [jmID] [章节数]”指定章节")
                    ]))
                    chap = "-1"
                match ctx.event.query.launcher_type:
                    case LauncherTypes.GROUP:
                        message_data = {
                            "group_id": str(ctx.event.launcher_id),
                            "file": os.path.normpath(os.path.join(self.pdf_dir, f"{searchManga(manga_id)}{chap}.pdf")),
                            "name": f"{manga_id}{chap}.pdf",
                        }
                    case LauncherTypes.PERSON:
                        message_data = {
                            "user_id": str(ctx.event.sender_id),
                            "file": os.path.normpath(os.path.join(self.pdf_dir, f"{searchManga(manga_id)}{chap}.pdf")),
                            "name": f"{manga_id}{chap}.pdf",
                        }
                await self.send_file.send(message_data, ctx.event.query.launcher_type)
            case "/jm [ID] [CHAPTER]":
                manga_id = re.search(r"^/jm (\d+) (\d+)$", msg).group(1)
                chap = int(re.search(r"^/jm (\d+) (\d+)$", msg).group(2))
                await ctx.reply(MessageChain([
                    Plain(f"正在将jm{manga_id}章节{chap}转换为PDF...\n可能需要10s至1min不等，请耐心等待")
                ]))
                if not mangaCache(manga_id):
                    downloadManga(manga_id)
                manga_title = searchManga(manga_id)
                all2PDF(os.path.join(self.pdf_dir, manga_title), self.pdf_dir, f"{manga_title}-{chap}", chap)
                self.ap.logger.info("转换完成")
                match ctx.event.query.launcher_type:
                    case LauncherTypes.GROUP:
                        message_data = {
                            "group_id": str(ctx.event.launcher_id),
                            "file": os.path.normpath(os.path.join(self.pdf_dir, f"{manga_title}-{chap}.pdf")),
                            "name": f"{manga_id}-{chap}.pdf",
                        }
                    case LauncherTypes.PERSON:
                        message_data = {
                            "user_id": str(ctx.event.sender_id),
                            "file": os.path.normpath(os.path.join(self.pdf_dir, f"{manga_title}-{chap}.pdf")),
                            "name": f"{manga_id}-{chap}.pdf",
                        }
                await self.send_file.send(message_data, ctx.event.query.launcher_type)
            case _:
                pass
        
    # 插件卸载时触发
    def __del__(self):
        pass
