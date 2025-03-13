import requests
from typing import Dict, List, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import config

class OneThingAI:
    """OneThingAI 实例管理工具类"""
    """
    100: 启动中
    300: 运行中
    400: 停止中
    800: 已停止
    """
    BASE_URL = "https://api-lab.onethingai.com"
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {config.api_key}"
        }
        
        # 设置重试策略
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """发送 API 请求的通用方法"""
        url = f"{self.BASE_URL}{endpoint}"
        try:
            kwargs = {
                'headers': self.headers,
                'timeout': (5, 15)  # (连接超时, 读取超时)
            }
            
            if data is not None and method.upper() in ['POST', 'GET', 'PUT', 'DELETE']:
                kwargs['json'] = data
            
            response = self.session.request(method, url, **kwargs)
            
            # 检查响应状态
            if response.status_code == 401:
                raise Exception("认证失败：请检查 API 密钥是否正确")
            elif response.status_code == 403:
                raise Exception("权限不足：请检查 API 密钥权限")
            elif response.status_code == 404:
                raise Exception("资源不存在：请检查 API 端点是否正确")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.SSLError as e:
            raise Exception(f"SSL 证书验证失败: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"连接服务器失败: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise Exception(f"请求超时: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {str(e)}")
    
    def list_image(self) -> List[Dict]:
        """获取我的镜像列表"""
        return self._make_request("GET", "/api/v2/app/private/image/list")

    def list_resources(self, appImageId: str) -> List[Dict]:
        """资源拉取接口"""
        return self._make_request("GET", f"/api/v2/resources/?appImageId={appImageId}")

    def list_instances(self) -> List[Dict]:
        """获取实例列表"""
        return self._make_request("GET", "/api/v2/app")
    
    def start_instance(self, instance_id: str) -> Dict:
        """启动实例"""
        return self._make_request("PUT", f"/api/v1/app/operate/boot/{instance_id}")
    
    def stop_instance(self, instance_id: str) -> Dict:
        """停止实例"""
        return self._make_request("PUT", f"/api/v1/app/operate/shutdown/{instance_id}")
    
    def delete_instance(self, instance_id: str) -> Dict:
        """删除实例"""
        return self._make_request("DELETE", f"/api/v1/app/{instance_id}")
    
    def create_instance(self, config: Dict) -> Dict:
        """创建新实例"""
        return self._make_request("POST", "/api/v2/app", data=config)
    
    def get_wallet(self) -> Dict:
        """获取余额"""
        return self._make_request("GET", "/api/v1/account/wallet/detail")
