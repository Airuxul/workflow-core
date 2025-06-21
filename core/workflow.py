# -*- coding: utf-8 -*-

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type, Any

if TYPE_CHECKING:
    from core.manager import WorkflowManager
    from core.config import Config

class BaseWorkflow(ABC):
    """
    所有可执行单元（工作流）的抽象基类。
    """
    DEFAULT_PARAMS = {}
    def __init__(self, manager: WorkflowManager, config: Config):
        """
        初始化工作流。
        
        :param manager: 工作流管理器单例。
        :param config: 为此工作流实例创建的、已包含上层作用域的Config实例。
        """
        self.manager = manager
        self.config = config

    def log(self, message: str):
        """
        将日志消息委托给管理器进行打印。
        """
        self.manager.log(message)

    def run_flow(self, workflow_class: Type[BaseWorkflow], params: dict | None = None) -> Any:
        """方便地调用管理器来执行一个子流程。"""
        return self.manager.run_flow(workflow_class, flow_params=params)

    def set_shared_value(self, key: str, value):
        """方便地调用管理器来设置一个全局共享值。"""
        self.manager.set_shared_value(key, value)

    def get_param(self, key: str, default=None):
        """从当前工作流的配置作用域中获取参数。"""
        return self.config.get_param(key, default)

    @abstractmethod
    def run(self) -> Any:
        """
        工作流的执行入口，所有业务逻辑都应在此方法中定义。
        """
        pass 