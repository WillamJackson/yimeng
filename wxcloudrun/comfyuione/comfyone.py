import requests
from typing import Dict, List, Optional
import config

class ComfyOne:
    """ComfyOne API 调用工具类"""
    
    BASE_URL = "https://pandora-server-cf.onethingai.com"
    
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """发送 API 请求的通用方法"""
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data, timeout=5)
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
    
    
