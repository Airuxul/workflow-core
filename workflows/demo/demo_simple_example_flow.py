# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
from core.constants import WorkflowStatus
from workflows.system.bat_flow import BatFlow

class DemoSimpleExampleFlow(BaseWorkflow):
    """
    简单示例工作流，展示框架的基本用法。
    
    这个示例演示了：
    1. 如何定义默认参数
    2. 如何获取和使用参数
    3. 如何记录日志
    4. 如何调用子工作流
    5. 如何设置共享值
    """
    
    DEFAULT_PARAMS = {
        "user_name": "开发者",
        "greeting": "你好",
        "repeat_count": 3,
        "show_system_info": True
    }
    
    def run(self):
        """工作流的主要执行逻辑"""
        self.log("=" * 40)
        self.log("开始执行简单示例工作流")
        self.log("=" * 40)
        
        # 1. 获取参数
        user_name = self.get_param("user_name")
        greeting = self.get_param("greeting")
        repeat_count = self.get_param("repeat_count")
        show_system_info = self.get_param("show_system_info")
        
        # 2. 记录日志
        self.log(f"用户: {user_name}")
        self.log(f"问候语: {greeting}")
        self.log(f"重复次数: {repeat_count}")
        
        # 3. 执行循环操作
        for i in range(repeat_count):
            self.log(f"[{i + 1}/{repeat_count}] {greeting}，{user_name}！")
        
        # 4. 设置共享值
        self.set_shared_value("last_greeting", f"{greeting}，{user_name}")
        self.set_shared_value("execution_count", repeat_count)
        
        # 5. 条件执行
        if show_system_info:
            self.log("显示系统信息:")
            self.run_flow(BatFlow, {
                "cmd": "echo 演示系统命令执行",
                "wait": True
            })
        
        # 6. 使用共享值
        last_greeting = self.manager.get_shared_value("last_greeting")
        execution_count = self.manager.get_shared_value("execution_count")
        
        self.log("执行统计:")
        self.log(f"  最后问候: {last_greeting}")
        self.log(f"  执行次数: {execution_count}")
        
        # 7. 返回结果
        result = {
            "status": WorkflowStatus.SUCCESS.value,
            "user_name": user_name,
            "greeting": greeting,
            "execution_count": execution_count,
            "message": "简单示例工作流执行完成"
        }
        
        self.log("=" * 40)
        self.log("简单示例工作流执行完成")
        self.log("=" * 40)
        
        return result 