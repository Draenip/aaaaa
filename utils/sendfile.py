import json
import aiohttp
from pkg.core.entities import LauncherTypes

class send_file():
    def __init__(self, host: str, port: int):
        self.url = f"http://{host}:{port}"

    async def send(self, message_data: dict, launcher_type: LauncherTypes):
        '''
        发送文件
        
        args:
            message_data: dict, 包含文件信息的字典
            launcher_type: LauncherTypes, 发送者类型
            
        return:
            None
        '''
        headers = {
            'Content-Type': 'application/json'
        }
        api_url = ""
        match launcher_type:
            case LauncherTypes.GROUP:
                api_url = "/upload_group_file"
            case LauncherTypes.PERSON:
                api_url = "/upload_private_file"
        payload = json.dumps(message_data)
        async with aiohttp.ClientSession(self.url, headers=headers) as session:
            async with session.post(api_url, data=payload) as response:
                await response.json()
                print(response)