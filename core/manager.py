# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Type, Any
from core.config import Config
from core.workflow import BaseWorkflow

class WorkflowManager:
    def __init__(self, cli_params: dict | None = None):
        cli_params = cli_params or {}
        
        self._shared_context = {}
        shared_config = Config(params=self._shared_context, parent=None)
        self.global_config = Config(params=cli_params, parent=shared_config)
        self.call_stack = set()
        self._config_stack = [self.global_config]
        self.flow_depth = -1 # 深度计数器，从-1开始

    @property
    def _current_config(self) -> Config:
        return self._config_stack[-1]

    def log(self, message: str):
        """
        以当前工作流的正确缩进级别打印日志消息。
        """
        indent = '\t' * (self.flow_depth if self.flow_depth > 0 else 0)
        print(f"{indent}{message}")

    def set_shared_value(self, key: str, value):
        self._shared_context[key] = value

    def run_flow(self, workflow_class: Type[BaseWorkflow], flow_params: dict | None = None) -> Any:
        if workflow_class in self.call_stack:
            self.log(f"错误：检测到循环依赖！工作流 '{workflow_class.__name__}' 已在调用栈中。")
            return
        
        self.call_stack.add(workflow_class)
        self.flow_depth += 1 # 运行前深度+1
        
        flow_config = None

        try:
            default_params = getattr(workflow_class, "DEFAULT_PARAMS", {})
            all_flow_params = {**default_params, **(flow_params or {})}
            flow_config = Config(params=all_flow_params, parent=self._current_config)
            self._config_stack.append(flow_config)
            
            self.log(f"--- 开始执行工作流: {workflow_class.__name__} ---")
            workflow_instance = workflow_class(manager=self, config=flow_config)
            result = workflow_instance.run()
            self.log(f"--- 工作流: {workflow_class.__name__} 执行完毕 ---")
            return result

        except Exception as e:
            self.log(f"执行工作流 '{workflow_class.__name__}' 时发生未知错误: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if flow_config and self._config_stack and self._config_stack[-1] is flow_config:
                 self._config_stack.pop()
            if workflow_class in self.call_stack:
                self.call_stack.remove(workflow_class)
            self.flow_depth -= 1 # 运行后深度-1