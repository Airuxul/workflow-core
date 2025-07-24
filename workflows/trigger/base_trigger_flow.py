# -*- coding: utf-8 -*-
import time
from core.workflow import BaseWorkflow
from workflows.system.bat_flow import BatFlow

class TriggerWorkflow(BaseWorkflow):
    """
    触发器型工作流：run时while监听，满足条件时自动触发目标workflow。
    子类需实现should_trigger()和get_target_params()。
    """
    TARGET_WORKFLOW = None  # 需指定目标workflow类

    DEFAULT_PARAMS = {
        "trigger_workflow_data": None,
        "sleep_interval": 1,
    }

    def update_trigger(self) -> bool:
        """
        更新触发器状态
        """
        raise NotImplementedError

    def run(self):
        self.will_trigger = False
        if not self.get_param("trigger_workflow_data"):
            self.log("trigger_workflow_data 参数未设置，无法启动触发器")
            return
        trigger_workflow_data = self.get_param("trigger_workflow_data")
        sleep_interval = self.get_param("sleep_interval")
        self.log(f"触发器启动，监听中... 检查间隔: {sleep_interval}s")
        while True:
            self.update_trigger()
            if self.will_trigger:
                self.log("检测到触发条件，启动目标workflow...")
                self.run_flow(BatFlow, params={
                    "wait": False,
                    "cmd": f"uv run main.py --workflow_data {trigger_workflow_data}",
                })
                self.will_trigger = False
            time.sleep(sleep_interval) 