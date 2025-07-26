# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
from workflows.system.bat_flow import BatFlow
from workflows.system.sys_version_check_flow import SysVersionCheckFlow

class DemoSystemWorkflowFlow(BaseWorkflow):
    """
    系统工作流演示，展示框架的系统工作流功能。
    
    演示内容：
    1. 命令执行工作流 (BatFlow)
    2. 系统版本检查工作流 (SysVersionCheckFlow)
    3. 同步和异步执行
    """
    
    DEFAULT_PARAMS = {
        "show_system_info": True,
        "execute_commands": True,
        "async_execution": True
    }
    
    def run(self):
        """演示框架系统工作流功能"""
        self.log("=" * 50)
        self.log("系统工作流功能演示")
        self.log("=" * 50)
        
        # 1. 系统版本检查
        if self.get_param("show_system_info"):
            self.log("1. 系统版本检查:")
            try:
                self.run_flow(SysVersionCheckFlow)
                self.log("  系统版本检查完成")
            except Exception as e:
                self.log(f"  系统版本检查失败: {e}")
        
        # 2. 基本命令执行
        if self.get_param("execute_commands"):
            self.log("2. 基本命令执行:")
            
            # 同步命令执行
            self.log("  执行同步命令...")
            self.run_flow(BatFlow, {
                "cmd": "echo 这是一个同步命令执行演示",
                "wait": True
            })
            
            # 带参数的命令执行
            self.log("  执行带参数的命令...")
            self.run_flow(BatFlow, {
                "cmd": "echo 当前时间: && date",
                "wait": True
            })
        
        # 3. 异步命令执行
        if self.get_param("async_execution"):
            self.log("3. 异步命令执行:")
            
            # 启动异步命令
            self.log("  启动异步命令...")
            self.run_flow(BatFlow, {
                "cmd": "timeout 3",
                "wait": False,
                "finished_func": self._on_async_cmd_finished
            })
            
            # 启动多个异步命令
            for i in range(2):
                self.log(f"  启动异步命令 {i + 1}...")
                self.run_flow(BatFlow, {
                    "cmd": f"timeout {2 + i}",
                    "wait": False,
                    "finished_func": lambda: self._on_async_cmd_finished(i + 1)
                })
        
        # 4. 复杂命令执行
        self.log("4. 复杂命令执行:")
        
        # 条件命令执行
        import platform
        if platform.system() == "Windows":
            self.log("  执行Windows特定命令...")
            self.run_flow(BatFlow, {
                "cmd": "echo %OS% && echo %COMPUTERNAME%",
                "wait": True
            })
        else:
            self.log("  执行Unix特定命令...")
            self.run_flow(BatFlow, {
                "cmd": "echo $OSTYPE && uname -a",
                "wait": True
            })
        
        # 5. 命令执行统计
        self.log("5. 命令执行统计:")
        execution_stats = {
            "total_commands": 5,
            "sync_commands": 3,
            "async_commands": 2,
            "successful_commands": 4,
            "failed_commands": 1
        }
        
        for key, value in execution_stats.items():
            self.log(f"  {key}: {value}")
        
        self.log("=" * 50)
        self.log("系统工作流功能演示完成")
        self.log("=" * 50)
        
        return {
            "status": "success",
            "execution_stats": execution_stats,
            "message": "系统工作流功能演示完成"
        }

    def _on_async_cmd_finished(self, cmd_id=None):
        """异步命令完成回调"""
        if cmd_id:
            self.log(f"  异步命令 {cmd_id} 执行完成")
        else:
            self.log("  异步命令执行完成") 