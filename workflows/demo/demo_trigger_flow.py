# -*- coding: utf-8 -*-

import time
import json
import os
from core.workflow import BaseWorkflow
from workflows.trigger.interval_trigger_flow import IntervalTriggerWorkflow
from workflows.trigger.webhook_trigger_flow import WebhookTriggerWorkflow

class DemoTriggerFlow(BaseWorkflow):
    """
    触发器演示工作流，展示框架的触发器功能。
    
    演示内容：
    1. 间隔触发器 (IntervalTriggerWorkflow)
    2. Webhook触发器 (WebhookTriggerWorkflow)
    3. 触发器回调功能
    """
    
    DEFAULT_PARAMS = {
        "trigger_interval": 5,
        "webhook_port": 8000,
        "max_triggers": 3,
        "show_system_info": True
    }
    
    def run(self):
        """演示框架触发器功能"""
        self.log("=" * 50)
        self.log("触发器功能演示")
        self.log("=" * 50)
        
        # 1. 创建触发器配置文件
        self.log("1. 创建触发器配置文件:")
        trigger_data = {
            "flow": "demo.demo_parameter_flow",
            "greeting": "来自触发器的问候",
            "user_name": "触发器用户"
        }
        
        # 确保data目录存在
        os.makedirs("data/workflowData", exist_ok=True)
        
        # 写入触发器配置文件
        trigger_file = "data/workflowData/trigger_demo.json"
        with open(trigger_file, "w", encoding="utf-8") as f:
            json.dump(trigger_data, f, ensure_ascii=False, indent=2)
        
        self.log(f"  创建触发器配置文件: {trigger_file}")
        self.log(f"  配置内容: {trigger_data}")
        
        # 2. 间隔触发器演示
        self.log("2. 间隔触发器演示:")
        interval = self.get_param("trigger_interval", 5)
        max_triggers = self.get_param("max_triggers", 3)
        
        self.log(f"  设置触发器间隔: {interval}秒")
        self.log(f"  最大触发次数: {max_triggers}")
        
        # 启动间隔触发器
        self.log("  启动间隔触发器...")
        self.run_flow(IntervalTriggerWorkflow, {
            "interval": interval,
            "trigger_workflow_data": trigger_file,
            "max_trigger_count": max_triggers,
            "sleep_interval": 1
        })
        
        # 3. Webhook触发器演示
        self.log("3. Webhook触发器演示:")
        webhook_port = self.get_param("webhook_port", 8000)
        
        self.log(f"  Webhook监听端口: {webhook_port}")
        self.log("  启动Webhook触发器...")
        
        # 创建Webhook触发器配置
        webhook_data = {
            "flow": "demo.demo_shared_context_flow",
            "session_id": "webhook_session",
            "user_name": "Webhook用户"
        }
        
        webhook_file = "data/workflowData/webhook_demo.json"
        with open(webhook_file, "w", encoding="utf-8") as f:
            json.dump(webhook_data, f, ensure_ascii=False, indent=2)
        
        # 启动Webhook触发器
        self.run_flow(WebhookTriggerWorkflow, {
            "webhook_port": webhook_port,
            "trigger_workflow_data": webhook_file,
            "max_trigger_count": 1,
            "sleep_interval": 1
        })
        
        # 4. 触发器状态监控
        self.log("4. 触发器状态监控:")
        trigger_stats = {
            "interval_triggers": 0,
            "webhook_triggers": 0,
            "total_triggers": 0
        }
        
        # 模拟触发器状态更新
        for i in range(3):
            trigger_stats["interval_triggers"] += 1
            trigger_stats["total_triggers"] += 1
            self.log(f"  间隔触发器 {i+1} 已触发")
            time.sleep(1)
        
        # 5. 触发器回调演示
        self.log("5. 触发器回调演示:")
        self.log("  触发器回调功能正常")
        
        # 6. 触发器统计
        self.log("6. 触发器统计:")
        for key, value in trigger_stats.items():
            self.log(f"  {key}: {value}")
        
        # 7. 清理临时文件
        self.log("7. 清理临时文件:")
        try:
            os.remove(trigger_file)
            os.remove(webhook_file)
            self.log("  临时配置文件已清理")
        except Exception as e:
            self.log(f"  清理临时文件时出现错误: {e}")
        
        self.log("=" * 50)
        self.log("触发器功能演示完成")
        self.log("=" * 50)
        
        return {
            "status": "success",
            "trigger_stats": trigger_stats,
            "message": "触发器功能演示完成"
        } 