# -*- coding: utf-8 -*-

import time
import threading
from core.workflow import BaseWorkflow
from core.constants import WorkflowStatus
from workflows.system.bat_flow import BatFlow

class DemoAsyncFlow(BaseWorkflow):
    """
    异步执行演示工作流，展示框架的异步执行功能。
    
    演示内容：
    1. 异步命令执行
    2. 异步任务回调
    3. 异步任务状态监控
    """
    
    DEFAULT_PARAMS = {
        "task_count": 3,
        "task_duration": 2,
        "show_progress": True
    }
    
    def __init__(self, manager, config):
        super().__init__(manager, config)
        self.completed_tasks = 0
        self.total_tasks = 0
        self.task_results = {}

    def run(self):
        """演示框架异步执行功能"""
        self.log("=" * 50)
        self.log("异步执行功能演示")
        self.log("=" * 50)
        
        # 1. 异步命令执行
        self.log("1. 异步命令执行:")
        self.run_flow(BatFlow, {
            "cmd": "timeout 3",
            "wait": False,
            "finished_func": self._on_async_cmd_finished
        })
        
        # 2. 多线程异步任务
        self.log("2. 多线程异步任务:")
        self.total_tasks = self.get_param("task_count", 3)
        task_duration = self.get_param("task_duration", 2)
        
        for i in range(self.total_tasks):
            self._start_async_task(i + 1, task_duration)
        
        # 3. 监控异步任务进度
        self.log("3. 任务进度监控:")
        while self.completed_tasks < self.total_tasks:
            progress = (self.completed_tasks / self.total_tasks) * 100
            self.log(f"  进度: {self.completed_tasks}/{self.total_tasks} ({progress:.1f}%)")
            time.sleep(1)
        
        self.log("  所有异步任务已完成")
        
        # 4. 显示任务结果
        self.log("4. 任务执行结果:")
        for task_id, result in self.task_results.items():
            self.log(f"  任务 {task_id}: {result}")
        
        # 5. 异步任务统计
        self.log("5. 异步任务统计:")
        self.log(f"  总任务数: {self.total_tasks}")
        self.log(f"  完成任务数: {self.completed_tasks}")
        self.log(f"  成功率: {(self.completed_tasks / self.total_tasks) * 100:.1f}%")
        
        self.log("=" * 50)
        self.log("异步执行功能演示完成")
        self.log("=" * 50)
        
        return {
            "status": WorkflowStatus.SUCCESS.value,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "task_results": self.task_results,
            "success_rate": (self.completed_tasks / self.total_tasks) * 100
        }

    def _start_async_task(self, task_id, duration):
        """启动异步任务"""
        def async_task():
            try:
                start_time = time.time()
                self.log(f"  任务 {task_id} 开始执行...")
                
                # 模拟耗时操作
                time.sleep(duration)
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # 设置任务结果
                result = {
                    "task_id": task_id,
                    "status": "completed",
                    "start_time": time.strftime("%H:%M:%S", time.localtime(start_time)),
                    "end_time": time.strftime("%H:%M:%S", time.localtime(end_time)),
                    "execution_time": f"{execution_time:.2f}s"
                }
                
                self.task_results[task_id] = result
                self.log(f"  任务 {task_id} 执行完成 (耗时: {execution_time:.2f}s)")
                
            except Exception as e:
                self.log(f"  任务 {task_id} 执行失败: {e}")
                self.task_results[task_id] = {
                    "task_id": task_id,
                    "status": "failed",
                    "error": str(e)
                }
            finally:
                self.completed_tasks += 1
        
        thread = threading.Thread(target=async_task, daemon=True)
        thread.start()

    def _on_async_cmd_finished(self):
        """异步命令完成回调"""
        self.log("  异步命令执行完成") 