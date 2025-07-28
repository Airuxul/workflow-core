# -*- coding: utf-8 -*-

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type, Any
import time

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

    @classmethod
    def default_params(cls) -> dict:
        """
        返回当前类及其所有父类的默认参数合并结果。
        子类可重写本方法并返回自己的默认参数，父类参数会自动合并。
        """
        params = {}
        for base in reversed(cls.__mro__):
            if hasattr(base, 'DEFAULT_PARAMS'):
                params.update(getattr(base, 'DEFAULT_PARAMS'))
        return params

    def log(self, *args, **kwargs):
        self.manager.log(*args, **kwargs)

    def run_flow(self, workflow_class: Type[BaseWorkflow], params: dict | None = None) -> Any:
        """方便地调用管理器来执行一个子流程。"""
        return self.manager.run_flow(workflow_class, flow_params=params)

    def set_shared_value(self, key: str, value):
        """方便地调用管理器来设置一个全局共享值。"""
        self.manager.set_shared_value(key, value)

    def get_param(self, key: str, default=None):
        """从当前工作流的配置作用域中获取参数。"""
        return self.config.get_param(key, default)

    def init(self):
        """初始化工作流。"""
        pass

    @abstractmethod
    def run(self) -> Any:
        """
        工作流的执行入口，所有业务逻辑都应在此方法中定义。
        """
        pass

class TriggerWorkflow(BaseWorkflow):
    """
    触发器型工作流：run时while监听，满足条件时自动触发目标workflow。
    子类需实现should_trigger()和get_target_params()。
    """
    TARGET_WORKFLOW = None  # 需指定目标workflow类
    CHECK_INTERVAL = 1      # 检查间隔秒数

    def should_trigger(self) -> bool:
        """
        判断是否满足触发条件。子类实现。
        """
        raise NotImplementedError

    def get_target_params(self) -> dict:
        """
        获取目标workflow的参数。子类实现。
        """
        raise NotImplementedError

    def run(self):
        self.log("触发器启动，监听中...")
        while True:
            if self.should_trigger():
                self.log("检测到触发条件，启动目标workflow...")
                self.run_flow(self.TARGET_WORKFLOW, self.get_target_params())
            time.sleep(self.CHECK_INTERVAL) 