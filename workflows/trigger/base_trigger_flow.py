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
        "max_trigger_count": -1,
        "max_running_work_count": -1,
    }

    def __init__(self, manager, config):
        super().__init__(manager, config)
        self.total_trigger_count = 0
        self.running_work_count = 0
        self.will_trigger = False

    def update_trigger(self) -> bool:
        """
        更新触发器状态
        """
        raise NotImplementedError

    def run(self):
        trigger_workflow_data = self.get_param("trigger_workflow_data")
        if not trigger_workflow_data:
            self.log("trigger_workflow_data 参数未设置，无法启动触发器")
            return
        sleep_interval = self.get_param("sleep_interval")
        if sleep_interval <= 0:
            self.log("sleep_interval 参数必须大于0")
            return
        max_trigger_count = self.get_param("max_trigger_count")
        max_running_work_count = self.get_param("max_running_work_count")
        self.log(f"触发器启动，监听中... 检查间隔: {sleep_interval}s 最大触发次数: {max_trigger_count}")
        while True:
            if self.check_max_trigger_count(max_trigger_count):
                self.log(f"触发器达到最大触发次数{max_trigger_count}，停止监听")
                break
            time.sleep(sleep_interval) # 检查间隔
            self.update_trigger()
            if not self.will_trigger:
                continue
            if self.check_max_running_work_count(max_running_work_count):
                self.log(f"目标workflow运行数量达到最大值{max_trigger_count}，等待目标workflow运行完毕...")
                continue
            self.log("检测到触发条件，启动目标workflow...")
            self.run_flow(BatFlow, params={
                "wait": False,
                "cmd": f"uv run main.py --workflow_data {trigger_workflow_data}",
                "finished_func": self.on_trigger_workflow_finished,
            })
            self.running_work_count += 1
            self.will_trigger = False

    def on_trigger_workflow_finished(self):
        self.running_work_count -= 1
        self.total_trigger_count += 1

    def check_max_trigger_count(self, max_trigger_count):
        return max_trigger_count != -1 and self.total_trigger_count >= max_trigger_count

    def check_max_running_work_count(self, max_running_work_count):
        return max_running_work_count != -1 and self.running_work_count >= max_running_work_count
