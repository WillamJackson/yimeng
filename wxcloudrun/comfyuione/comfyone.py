import os
import sys
import requests
import asyncio
import websockets
import json
from typing import Dict, List, Optional, Callable

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

import config

class ComfyOne:
    """ComfyOne API 调用工具类"""
    
    BASE_URL = "https://pandora-server-cf.onethingai.com"
    WS_URL = "wss://pandora-server-cf.onethingai.com/v1/ws"
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {config.api_key}"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict:
        """发送 API 请求的通用方法"""
        url = f"{self.BASE_URL}{endpoint}"
        try:
            if files:
                # 文件上传请求使用更长的超时时间（30秒）
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    files=files,
                    timeout=30  # 增加超时时间到30秒
                )
            else:
                # 普通请求使用默认超时时间
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    timeout=5
                )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {str(e)}")
    
    def list_backends(self) -> Dict:
        """获取所有可用的后端服务实例"""
        return self._make_request("GET", "/v1/backends")
    
    def register_backend(self, instance_id: str) -> Dict:
        """注册一个新的后端服务实例"""
        data = {"instance_id": instance_id}
        return self._make_request("POST", "/v1/backends", data)
    
    def create_workflow(self, name: str, inputs: List[Dict], outputs: List[str], workflow: Dict) -> Dict:
        """创建一个新的工作流"""
        data = {
            "name": name,
            "inputs": inputs,
            "outputs": outputs,
            "workflow": workflow
        }
        return self._make_request("POST", "/v1/workflows", data)
    
    def upload_image(self, image_path: str) -> Dict:
        """上传图片到服务器
        Args:
            image_path (str): 图片文件的本地路径
        Returns:
            Dict: 服务器响应，包含上传结果
        """
        try:
            with open(image_path, 'rb') as image_file:
                # 获取文件名
                file_name = os.path.basename(image_path)
                # 创建文件元组：(文件名, 文件对象, MIME类型)
                files = {
                    'file': (file_name, image_file, 'image/png')  # 或 'image/jpeg' 等根据实际文件类型
                }
                return self._make_request(
                    method="POST",
                    endpoint="/v1/files",
                    files=files
                )
        except FileNotFoundError:
            raise Exception(f"文件未找到: {image_path}")
        except Exception as e:
            raise Exception(f"图片上传失败: {str(e)}")
    
    def submit_task(self, workflow_id: str, inputs: List[Dict], free_cache: bool = False) -> Dict:
        """提交绘画任务"""
        data = {
            "workflow_id": workflow_id,
            "inputs": inputs,
            "free_cache": free_cache
        }
        return self._make_request("POST", "/v1/prompts", data) 
    
    def submit_workflow_task(self, workflow) -> str:
        """提交工作流任务"""
        return self._make_request("POST", "/v1/prompts_workflow", workflow) 

    def get_task_status(self, task_id: str) -> Dict:
        """获取任务状态"""
        return self._make_request("GET", f"/v1/prompts/{task_id}/status") 
    
    def get_task_images(self, image_url: str) -> Dict:
        """获取任务图片"""
        # 截取 image_url 中的路径部分
        url_path = image_url.split("https://pandora-server-cf.onethingai.com")[-1]
        return self._make_request("GET", url_path)

    async def listen_task_status(self, callback: Optional[Callable] = None):
        """监听任务状态
        Args:
            callback: 回调函数，用于处理接收到的消息
        """
        async def default_callback(message):
            """默认的回调函数"""
            try:
                data = json.loads(message)
                print(data)
                if data['type'] == 'pendding':
                    current = data.get('data', {}).get('current', 'unknown')
                    print(f"任务 {data.get('taskId')} 等待执行, 当前位置: {current}")
                elif data['type'] == 'progress':
                    process = data.get('data', {}).get('process', 0)
                    print(f"任务 {data.get('taskId')} 正在执行, 进度: {process}%")
                elif data['type'] == 'finished':
                    success = data.get('data', {}).get('success', False)
                    if success:
                        print(f"任务 {data.get('taskId')} 执行完成")
                    else:
                        print(f"任务 {data.get('taskId')} 执行失败")
                elif data['type'] == 'error':
                    message = data.get('data', {}).get('message', '未知错误')
                    print(f"任务执行出错: {message}")
            except json.JSONDecodeError:
                print(f"解析消息失败: {message}")
            except Exception as e:
                print(f"处理消息时出错: {str(e)}")

        while True:  # 添加外层循环，在连接断开时自动重连
            try:
                # 修改连接参数
                async with websockets.connect(
                    self.WS_URL,
                    extra_headers={
                        'Authorization': f'Bearer {config.api_key}'
                    },
                    ping_interval=None,  # 禁用自动 ping
                    ping_timeout=None,   # 禁用 ping 超时
                    close_timeout=10     # 设置关闭超时
                ) as websocket:
                    print("WebSocket 连接已建立")
                    
                    # 创建保活任务
                    async def heartbeat():
                        while True:
                            try:
                                await websocket.pong()
                                await asyncio.sleep(5)  # 每5秒发送一次pong
                            except:
                                return

                    heartbeat_task = asyncio.create_task(heartbeat())
                    
                    try:
                        while True:
                            try:
                                message = await websocket.recv()
                                if callback:
                                    await callback(message)
                                else:
                                    await default_callback(message)
                            except websockets.ConnectionClosed:
                                print("WebSocket 连接已关闭，准备重新连接...")
                                break
                            except Exception as e:
                                print(f"处理消息时出错: {str(e)}")
                                continue
                    finally:
                        heartbeat_task.cancel()
                    
            except Exception as e:
                print(f"WebSocket 连接出错: {str(e)}")
                print("5秒后尝试重新连接...")
                await asyncio.sleep(5)

    def start_listening(self):
        """启动 WebSocket 监听"""
        try:
            asyncio.run(self.listen_task_status())
        except KeyboardInterrupt:
            print("监听已手动停止")
        except Exception as e:
            print(f"监听出错: {str(e)}")
