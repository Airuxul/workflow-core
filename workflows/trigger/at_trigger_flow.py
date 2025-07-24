# -*- coding: utf-8 -*-
from .base_trigger_flow import TriggerWorkflow
import datetime

class AtTriggerWorkflow(TriggerWorkflow):
    """
    定时触发器，到达指定时间点触发一次。
    需设置trigger_time（datetime对象或ISO字符串）。
    """
    DEFAULT_PARAMS = {
        "trigger_time": "2025-07-24 10:00:00",
    }

    def update_trigger(self):
        trigger_time = self.get_param("trigger_time")
        if not trigger_time:
            self.log("trigger_time 参数未设置，无法启动触发器")
            return False
        if isinstance(trigger_time, str):
            trigger_dt = datetime.datetime.fromisoformat(trigger_time)
        else:
            trigger_dt = trigger_time
        self.will_trigger = datetime.datetime.now() >= trigger_dt