from ..onethingai.onething_ai import OneThingAI
from ..comfyuione.comfyone import ComfyOne
import time
import requests
import json

class DrawingTool:
    """画画工具类，用于启动 OneThingAI 实例"""
    
    def __init__(self):
        self.one_thing_ai = OneThingAI()
    
    def get_instance(self):
        """启动 OneThingAI 实例"""
        # 查询余额
        wallet_response = self.one_thing_ai.get_wallet()
        balance = float(wallet_response['data']['availableBalance'])
        print(f"当前余额: {balance}元")
        
        # 如果余额不足20元，发送通知
        if balance < 20:
            json = {
                "msgtype": "text",
                "text": {
                    "content": f"当前余额不足20元，仅剩{balance}元，请及时充值。"
                }
            }
            header = {
                "Content-Type": "application/json"
            }
            resp = requests.post(url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=3234d8bf-bb64-4e40-997e-9e756c232ad4', json=json, headers=header)
        # Step 1: 查询镜像
        image_response = self.one_thing_ai.list_image()
        app_image_id = image_response['data']['privateImageList'][0]['appImageId']
        print(f"获取到的镜像 ID: {app_image_id}")
        
        # 检查是否已有运行中的实例
        instances_response = self.one_thing_ai.list_instances()
        instances = [inst for inst in instances_response['data']['appList'] 
                    if inst['appImageId'] == app_image_id]
        
        # 检查是否有启动中或运行中的实例
        running_instances = [inst for inst in instances if inst['status'] in [100, 300]]
        if running_instances:
            instance = running_instances[0]
            # 如果实例正在启动中,等待其完全启动
            while instance['status'] == 100:
                time.sleep(3)
                instances_response = self.one_thing_ai.list_instances()
                instance = next(inst for inst in instances_response['data']['appList'] 
                              if inst['appId'] == instance['appId'])
            return instance['appId']
            
        # 检查是否有停止中或已停止的实例
        stopped_instances = [inst for inst in instances if inst['status'] in [400, 800]]
        if stopped_instances:
            instance = stopped_instances[0]
            # 如果实例正在停止中,等待其完全停止
            while instance['status'] == 400:
                time.sleep(3)
                instances_response = self.one_thing_ai.list_instances()
                instance = next(inst for inst in instances_response['data']['appList'] 
                              if inst['appId'] == instance['appId'])
            # 启动实例
            self.one_thing_ai.start_instance(instance['appId'])
            return instance['appId']
        
        if running_instances:
            # 如果有运行中的实例,直接返回第一个实例的ID
            instance_id = running_instances[0]['appId']
            print(f"找到运行中的实例 ID: {instance_id}")
            return instance_id
        # Step 2: 拉取资源
        resources_response = self.one_thing_ai.list_resources(app_image_id)
        available_resources = [r for r in resources_response['data']['resourceList'] 
                               if r['gpuType'] in ["NVIDIA-GEFORCE-RTX-4090", "NVIDIA-GEFORCE-RTX-3090"] 
                               and r['maxGpuNum'] > 0]
        if not available_resources:
            return None
        selected_resource = available_resources[0]
        print(f"选择的资源: {selected_resource}")
        
        # Step 3: 创建实例
        instance_config = {
            "appImageId": app_image_id,
            "gpuType": selected_resource['gpuType'],
            "regionId": selected_resource['regionId'],
            "billType": 3,
            "gpuNum": 1
        }
        create_instance_response = self.one_thing_ai.create_instance(instance_config)
        instance_id = create_instance_response['data']['appId']
        print(f"创建的实例 ID: {instance_id}")
        
        # Step 4: 等待实例启动
        while True:
            time.sleep(3)
            instance_status_response = self.one_thing_ai.list_instances()
            instance = next((inst for inst in instance_status_response['data']['appList'] if inst['appId'] == instance_id), None)
            status = instance['status']
            print(f"实例状态: {status}")
            if status == 300:
                print("实例启动成功")
                return instance['appId']
            
    def stop_and_release_instance(self, instance_id: str):
        """停止并释放 OneThingAI 实例"""
        # 检查实例状态
        instance_status_response = self.one_thing_ai.list_instances()
        instance = next((inst for inst in instance_status_response['data']['appList'] if inst['appId'] == instance_id), None)
        
        if not instance:
            print("实例不存在")
            return
            
        # 处理不同状态的实例
        status = instance['status']
        if status == 800:
            print("实例已经是关机状态,直接释放资源")
            self.one_thing_ai.delete_instance(instance_id)
            print("实例释放完成")
            return
        elif status == 300:
            print(f"实例正在运行,开始停止实例: {instance_id}")
            self.one_thing_ai.stop_instance(instance_id)
        else:
            print(f"实例处于中间状态 {status},等待其变为可操作状态...")
            while True:
                time.sleep(3)
                instance_status_response = self.one_thing_ai.list_instances()
                instance = next((inst for inst in instance_status_response['data']['appList'] if inst['appId'] == instance_id), None)
                if not instance:
                    print("实例不存在")
                    return
                    
                status = instance['status']
                print(f"当前实例状态: {status}")
                if status == 800:
                    print("实例已关机,准备释放资源")
                    self.one_thing_ai.delete_instance(instance_id)
                    print("实例释放完成")
                    return
                elif status == 300:
                    print("实例已运行,开始停止")
                    self.one_thing_ai.stop_instance(instance_id)
                    break
        
        # 等待实例停止
        while True:
            time.sleep(3)
            instance_status_response = self.one_thing_ai.list_instances()
            instance = next((inst for inst in instance_status_response['data']['appList'] if inst['appId'] == instance_id), None)
            if not instance:
                print("实例不存在")
                return
                
            status = instance['status']
            print(f"实例状态: {status}")
            if status == 800:
                print("实例已停止,准备释放资源")
                break
        
        # 释放实例
        print(f"正在释放实例: {instance_id}")
        self.one_thing_ai.delete_instance(instance_id)
        print("实例释放完成")

    def create_backend_instance(self):
        """创建后端服务实例"""
        # 检查是否有正在运行的 OneThingAI 实例
        instance_id = self.get_instance()
        print(f"获取到的 OneThingAI 实例 ID: {instance_id}")
        
        # 创建 ComfyOne 实例
        comfyone = ComfyOne()
        
        # 检查是否有运行中的 ComfyOne 实例
        backends_response = comfyone.list_backends()
        backends = backends_response.get('data', [])
        
        if backends:
            backend_instance_id = backends[0]['name']
            print(f"已有运行中的 ComfyOne 实例 ID: {backend_instance_id}")
            return backend_instance_id
        else:
            # 创建新的 ComfyOne 实例
            new_backend_response = comfyone.register_backend(instance_id)
            new_backend_instance_id = new_backend_response['instance_id']
            print(f"创建新的 ComfyOne 实例 ID: {new_backend_instance_id}")
            return new_backend_instance_id
    
    def delete_backend_instance(self, backend_instance_id: str):
        """删除后端服务实例"""
        # 创建 ComfyOne 实例
        comfyone = ComfyOne()
        
        # 删除指定的 ComfyOne 实例
        try:
            response = comfyone._make_request("DELETE", f"/v1/backends/{backend_instance_id}")
            print(f"删除 ComfyOne 实例 ID: {backend_instance_id} 成功")
            return response
        except Exception as e:
            print(f"删除 ComfyOne 实例 ID: {backend_instance_id} 失败: {str(e)}")
            return None
    
    def create_workflow_task_base(self):
        """创建工作流任务"""
        # 检查是否有后端服务实例
        comfyone = ComfyOne()
        backends_response = comfyone.list_backends()
        backends = backends_response.get('data', [])
        
        if not backends:
            # 如果没有后端服务实例，则创建一个
            backend_instance_id = self.create_backend_instance()
            print(f"创建新的后端服务实例 ID: {backend_instance_id}")
        else:
            backend_instance_id = backends[0]['name']
            print(f"已有运行中的后端服务实例 ID: {backend_instance_id}")
        
        # 读取 base.json 文件内容
        with open('wxcloudrun/comfyui/jsons/base.json', 'r', encoding='utf-8') as file:
            base_data = json.load(file)
        
        # 提交任务
        task_response = comfyone.submit_workflow_task(base_data)
        task_id = task_response['data']['taskId']
        print(f"提交任务成功，任务 ID: {task_id}")
        
        return task_id
    
    def get_task_images(self, task_id: str):
        """通过 taskId 查询任务状态并获取图片"""
        # 创建 ComfyOne 实例
        comfyone = ComfyOne()
        
        # 查询任务状态
        try:
            task_status_response = comfyone.get_task_status(task_id)
            if task_status_response['code'] == 0:
                task_data = task_status_response['data']
                if task_data['status'] == 'finished' and task_data['message'] == 'success':
                    images = task_data['images']
                    print(f"任务 {task_id} 完成，获取到的图片: {images}")
                    return images
                else:
                    print(f"任务 {task_id} 未完成或失败，状态: {task_data['status']}，信息: {task_data['message']}")
                    return None
            else:
                print(f"查询任务 {task_id} 状态失败，错误码: {task_status_response['code']}，信息: {task_status_response['msg']}")
                return None
        except Exception as e:
            print(f"查询任务 {task_id} 状态时发生异常: {str(e)}")
            return None
        
    