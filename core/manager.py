# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Type, Any
import importlib
import json
from core.config import Config
from core.workflow import BaseWorkflow
from core.logger import WorkflowLogger
from core.utils import Utils
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

    def _handle_workflow_error(self, workflow_class: Type[BaseWorkflow], error: Exception):
        """统一的错误处理方法"""
        error_message = Utils.format_message(
            "执行工作流 '{workflow_name}' 时发生未知错误: {error}",
            workflow_name=workflow_class.__name__,
            error=error
        )
        self.log(error_message)
        WorkflowLogger.instance().exception(error)

    def _setup_workflow_execution(self, workflow_class: Type[BaseWorkflow], flow_params: dict | None = None):
        """设置工作流执行环境"""
        if workflow_class in self.call_stack:
            self.log(f"错误：检测到循环依赖！工作流 '{workflow_class.__name__}' 已在调用栈中。")
            return None, None

        self.call_stack.add(workflow_class)
        self.flow_depth += 1  # 运行前深度+1

        default_params = workflow_class.default_params()
        all_flow_params = Utils.merge_dicts(default_params, flow_params or {})
        flow_config = Config(params=all_flow_params, parent=self._current_config)
        self._config_stack.append(flow_config)

        return flow_config, workflow_class

    def _cleanup_workflow_execution(self, workflow_class: Type[BaseWorkflow], flow_config: Config):
        """清理工作流执行环境"""
        if flow_config and self._config_stack and self._config_stack[-1] is flow_config:
            self._config_stack.pop()
        if workflow_class in self.call_stack:
            self.call_stack.remove(workflow_class)
        self.flow_depth -= 1  # 运行后深度-1

    def run_flow(self, workflow_class: Type[BaseWorkflow], flow_params: dict | None = None) -> Any:
        flow_config = None

        try:
            # 设置执行环境
            flow_config, workflow_class = self._setup_workflow_execution(workflow_class, flow_params)
            if flow_config is None:
                return None

            # 工作流开始日志
            self.log(
                LOG_FLOW_START_FORMAT.format(name=workflow_class.__name__),
                tree_type=LogTreePreType.START,
            )
            
            # 执行工作流
            workflow_instance = workflow_class(manager=self, config=flow_config)
            workflow_instance.init()
            result = workflow_instance.run()
            
            # 工作流结束日志
            self.log(
                LOG_FLOW_END_FORMAT.format(name=workflow_class.__name__),
                tree_type=LogTreePreType.END,
            )
            return result

        except Exception as e:
            self._handle_workflow_error(workflow_class, e)
            return None
        finally:
            self._cleanup_workflow_execution(workflow_class, flow_config)

#region 工作流静态方法
    @staticmethod
    def find_workflow_class(flow_name: str):
        """
        支持目录.文件（如 demo.async_test_flow）格式，精确查找对应workflow类。
        """
        if '.' not in flow_name:
            raise ValueError("flow_name 必须为 '目录.文件' 格式，如 demo.main_test_flow")
        module_path = f"workflows.{flow_name.replace('-', '_')}"
        workflow_module = importlib.import_module(module_path)
        class_name = Utils.flow_name_to_class_name(flow_name.split('.')[-1])
        if hasattr(workflow_module, class_name):
            obj = getattr(workflow_module, class_name)
            if Utils.is_valid_workflow_class(obj):
                return obj
        raise AttributeError(f"在 '{flow_name}.py' 中未找到类名为 '{class_name}' 的 BaseWorkflow 子类。")

    @staticmethod
    def handle_workflow_error(error: Exception, context: str = "工作流执行"):
        """
        统一的错误处理方法
        
        :param error: 异常对象
        :param context: 错误上下文描述
        """
        logger = WorkflowLogger.instance()
        
        if isinstance(error, (FileNotFoundError, AttributeError)):
            logger.error(f"错误: {error}")
        else:
            logger.error(f"{context}时发生致命错误: {error}")
            import traceback
            traceback.print_exc()

    @staticmethod
    def run_workflow_from_json(json_path: str):
        """
        从json文件读取参数并执行工作流。
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            params = json.load(f)
        WorkflowManager.run_workflow_from_dict(params)

    @staticmethod
    def run_workflow_from_dict(params: dict):
        """
        直接用dict参数执行工作流。
        """
        flow_name = params.get('flow')
        if not flow_name:
            WorkflowLogger.instance().error("参数必须包含'flow'字段，且为工作流名称！")
            return
        
        cli_params = Utils.exclude_dict(params, ['flow'])
        
        try:
            main_workflow_class = WorkflowManager.find_workflow_class(flow_name)
            manager = WorkflowManager(cli_params=cli_params)
            manager.run_flow(workflow_class=main_workflow_class)
        except Exception as e:
            WorkflowManager.handle_workflow_error(e, f"执行工作流 '{flow_name}'")

    @staticmethod
    def run_workflow(params: dict):
        """
        工作流主入口。支持传入dict或通过flow_data字段指定json文件。
        """
        flow_data = params.get('flow_data')
        if flow_data:
            WorkflowManager.run_workflow_from_json(flow_data)
        else:
            WorkflowManager.run_workflow_from_dict(params)
#endregion