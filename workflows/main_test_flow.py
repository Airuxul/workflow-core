# -*- coding: utf-8 -*-

import time
from core.workflow import BaseWorkflow
from .sys_version_check_flow import SysVersionCheckFlow
from .param_printer_flow import ParamPrinterFlow
from .bat_flow import BatFlow

class MainTestFlow(BaseWorkflow):
    """
    一个用于演示主要功能的主工作流。
    现在所有的执行单元都是 "flow"。
    """
    
    DEFAULT_PARAMS = {
        "default_message": "这是一个在工作流级别定义的默认消息。"
    }

    def __init__(self, manager, config):
        super().__init__(manager, config)
        self.bat1_finished = False
        self.bat2_finished = False

    def run(self):
        # 1. 执行一个无参数的简单工作流
        self.run_flow(SysVersionCheckFlow)
        # 2. 打印一个来自工作流默认参数的消息
        self.run_flow(ParamPrinterFlow, params={"msg": "{{default_message}}"})
        # 3. 在运行时设置一个共享值
        self.set_shared_value("dynamic_message", "这是来自上一步的动态消息！")
        # 4. 执行一个工作流，并使用上一步动态设置的值
        self.run_flow(BatFlow, params={"cmd": "echo 动态消息是: {{dynamic_message}}"})
        # 5. 执行一个异步工作流
        self.run_flow(BatFlow, params={"cmd": "timeout 2", "wait": False, "finished_func": self.onBat1Finished})
        # 6. 执行一个异步工作流
        self.run_flow(BatFlow, params={"cmd": "timeout 4", "wait": False, "finished_func": self.onBat2Finished})
        while not self.bat1_finished or not self.bat2_finished:
            time.sleep(1)
        # 7. 再次打印
        self.run_flow(ParamPrinterFlow, params={"msg": "{{default_message}}"})

    def onBat1Finished(self):
        self.bat1_finished = True

    def onBat2Finished(self):
        self.bat2_finished = True