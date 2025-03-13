from flask import jsonify
from run import app
from .drawing_tool import DrawingTool

@app.route('/api/create_workflow_task_base', methods=['POST'])
def create_workflow_task_base():
    """API 接口：创建工作流任务"""
    try:
        # 初始化 DrawingTool
        tool = DrawingTool()
        
        # 调用 create_workflow_task_base 方法
        task_id = tool.create_workflow_task_base()
        
        # 返回成功响应
        return jsonify({
            'status': 'success',
            'task_id': task_id
        }), 200
    except Exception as e:
        # 返回错误响应
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500   