# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Type, Any
from core.config import Config
from core.workflow import BaseWorkflow
from core.logger import WorkflowLogger
from core.constants import (
    LOG_FLOW_START_FORMAT,
    LOG_FLOW_END_FORMAT,
    LOG_FLOW_START_TREE,
    LOG_FLOW_END_TREE,
    LOG_FLOW_MID_TREE,
    LogTreePreType,
    LOG_TREE_INDENT,
)


class WorkflowManager:
    def __init__(self, cli_params: dict | None = None):
        cli_params = cli_params or {}

        self._shared_context = {}
        shared_config = Config(params=self._shared_context, parent=None)
        self.global_config = Config(params=cli_params, parent=shared_config)
        self.call_stack = set()
        self._config_stack = [self.global_config]
        self.flow_depth = -1  # 深度计数器，从-1开始

    @property
    def _current_config(self) -> Config:
        return self._config_stack[-1]

    def log(self, *args, tree_type=LogTreePreType.MID, **kwargs):
        """
        以当前工作流的树状结构打印日志消息。
        tree_type: LogTreeType.START|MID|END，决定树状符号
        """
        prefix = self._get_tree_prefix(tree_type=tree_type)
        WorkflowLogger.instance().info(prefix + " ".join(str(a) for a in args))

    def _get_tree_prefix(self, tree_type=LogTreePreType.MID):
        """每层只加一次缩进和树状符号，支持LogTreeType三种类型。"""
        if self.flow_depth <= 0:
            return ""
        indent = LOG_TREE_INDENT * (self.flow_depth - 1)
        if tree_type == LogTreePreType.START:
            tree = LOG_FLOW_START_TREE
        elif tree_type == LogTreePreType.END:
            tree = LOG_FLOW_END_TREE
        else:
            tree = LOG_FLOW_MID_TREE
        return f"{indent}{tree}"

    def set_shared_value(self, key: str, value):
        self._shared_context[key] = value

    def run_flow(
        self, workflow_class: Type[BaseWorkflow], flow_params: dict | None = None
    ) -> Any:
        if workflow_class in self.call_stack:
            self.log(
                f"错误：检测到循环依赖！工作流 '{workflow_class.__name__}' 已在调用栈中。"
            )
            return

        self.call_stack.add(workflow_class)
        self.flow_depth += 1  # 运行前深度+1

        flow_config = None

        try:
            default_params = workflow_class.default_params()
            all_flow_params = {**default_params, **(flow_params or {})}
            flow_config = Config(params=all_flow_params, parent=self._current_config)
            self._config_stack.append(flow_config)

            # 工作流开始日志
            self.log(
                LOG_FLOW_START_FORMAT.format(name=workflow_class.__name__),
                tree_type=LogTreePreType.START,
            )
            workflow_instance = workflow_class(manager=self, config=flow_config)
            result = workflow_instance.run()
            # 工作流结束日志
            self.log(
                LOG_FLOW_END_FORMAT.format(name=workflow_class.__name__),
                tree_type=LogTreePreType.END,
            )
            return result

        except Exception as e:
            self.log(f"执行工作流 '{workflow_class.__name__}' 时发生未知错误: {e}")
            WorkflowLogger.instance().exception(e)
            return None
        finally:
            if (
                flow_config
                and self._config_stack
                and self._config_stack[-1] is flow_config
            ):
                self._config_stack.pop()
            if workflow_class in self.call_stack:
                self.call_stack.remove(workflow_class)
            self.flow_depth -= 1  # 运行后深度-1
