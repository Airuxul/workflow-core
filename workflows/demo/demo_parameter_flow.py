# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow

class DemoParameterFlow(BaseWorkflow):
    """
    参数演示工作流，展示框架的参数功能。
    
    演示内容：
    1. 参数获取和模板解析
    2. 参数覆盖和默认值
    3. 参数在子工作流中的使用
    """
    
    DEFAULT_PARAMS = {
        "greeting": "你好",
        "user_name": "开发者",
        "base_url": "https://api.example.com",
        "endpoint": "{{base_url}}/users",
        "message": "欢迎 {{user_name}} 使用框架",
        "timeout": 30,
        "retry_count": 3
    }
    
    def run(self):
        """演示框架参数功能"""
        self.log("=" * 50)
        self.log("参数功能演示")
        self.log("=" * 50)
        
        # 1. 基本参数获取
        self.log("1. 基本参数获取:")
        greeting = self.get_param("greeting")
        user_name = self.get_param("user_name")
        timeout = self.get_param("timeout")
        
        self.log(f"  问候语: {greeting}")
        self.log(f"  用户名: {user_name}")
        self.log(f"  超时时间: {timeout}")
        
        # 2. 参数模板解析
        self.log("2. 参数模板解析:")
        endpoint = self.get_param("endpoint")
        message = self.get_param("message")
        
        self.log(f"  API端点: {endpoint}")
        self.log(f"  动态消息: {message}")
        
        # 3. 参数覆盖演示
        self.log("3. 参数覆盖演示:")
        custom_greeting = self.get_param("custom_greeting", "默认问候语")
        custom_timeout = self.get_param("custom_timeout", 60)
        
        self.log(f"  自定义问候语: {custom_greeting}")
        self.log(f"  自定义超时: {custom_timeout}")
        
        # 4. 默认值处理
        self.log("4. 默认值处理:")
        non_existent = self.get_param("non_existent_param", "默认值")
        retry_count = self.get_param("retry_count")
        
        self.log(f"  不存在的参数: {non_existent}")
        self.log(f"  重试次数: {retry_count}")
        
        # 5. 显示所有参数
        self.log("5. 所有参数:")
        for key, value in self.config.params.items():
            self.log(f"  {key}: {value}")
        
        self.log("=" * 50)
        self.log("参数功能演示完成")
        self.log("=" * 50)
        
        return {
            "status": "success",
            "greeting": greeting,
            "user_name": user_name,
            "endpoint": endpoint,
            "message": message
        } 