# -*- coding: utf-8 -*-

import time
from core.workflow import BaseWorkflow
from core.constants import WorkflowStatus
from workflows.system.bat_flow import BatFlow

class DemoSharedContextFlow(BaseWorkflow):
    """
    共享上下文演示工作流，展示框架的共享上下文功能。
    
    演示内容：
    1. 设置和获取共享值
    2. 在子工作流中使用共享值
    3. 共享复杂数据结构
    """
    
    DEFAULT_PARAMS = {
        "session_id": "demo_session_123",
        "user_name": "演示用户",
        "show_system_info": True
    }
    
    def run(self):
        """演示框架共享上下文功能"""
        self.log("=" * 50)
        self.log("共享上下文功能演示")
        self.log("=" * 50)
        
        # 1. 设置基本共享值
        self.log("1. 设置基本共享值:")
        self.set_shared_value("demo_session_id", self.get_param("session_id"))
        self.set_shared_value("demo_user_name", self.get_param("user_name"))
        self.set_shared_value("demo_timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
        
        self.log(f"  会话ID: {self.get_param('demo_session_id')}")
        self.log(f"  用户名: {self.get_param('demo_user_name')}")
        self.log(f"  时间戳: {self.get_param('demo_timestamp')}")
        
        # 2. 设置复杂数据结构
        self.log("2. 设置复杂数据结构:")
        user_data = {
            "name": "演示用户",
            "role": "开发者",
            "permissions": ["read", "write", "execute"],
            "settings": {
                "theme": "dark",
                "language": "zh-CN",
                "notifications": True
            }
        }
        
        self.set_shared_value("demo_user_data", user_data)
        self.log(f"  用户数据: {self.get_param('demo_user_data')}")
        
        # 3. 在子工作流中使用共享值
        self.log("3. 在子工作流中使用共享值:")
        if self.get_param("show_system_info"):
            self.run_flow(BatFlow, {
                "cmd": "echo 会话ID: {{demo_session_id}} && echo 用户名: {{demo_user_name}}",
                "wait": True
            })
        
        # 4. 演示共享值的动态更新
        self.log("4. 动态更新共享值:")
        self.set_shared_value("demo_execution_count", 1)
        self.log(f"  初始执行次数: {self.get_param('demo_execution_count')}")
        
        # 模拟多次执行
        for i in range(3):
            current_count = self.get_param("demo_execution_count", 0)
            new_count = current_count + 1
            self.set_shared_value("demo_execution_count", new_count)
            self.log(f"  第{i+1}次更新执行次数: {new_count}")
        
        # 5. 获取并显示所有共享值
        self.log("5. 所有共享值:")
        shared_values = {
            "session_id": self.get_param("demo_session_id"),
            "user_name": self.get_param("demo_user_name"),
            "timestamp": self.get_param("demo_timestamp"),
            "user_data": self.get_param("demo_user_data"),
            "execution_count": self.get_param("demo_execution_count")
        }
        
        for key, value in shared_values.items():
            self.log(f"  {key}: {value}")
        
        self.log("=" * 50)
        self.log("共享上下文功能演示完成")
        self.log("=" * 50)
        
        return {
            "status": WorkflowStatus.SUCCESS.value,
            "shared_values": shared_values,
            "message": "共享上下文演示完成"
        } 