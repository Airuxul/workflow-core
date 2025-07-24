# -*- coding: utf-8 -*-
from .base_trigger_flow import TriggerWorkflow
import time

class IntervalTriggerWorkflow(TriggerWorkflow):
    """
    间隔触发器，每隔interval秒触发一次。
    """
    DEFAULT_PARAMS = {
        "interval": 10,
    }

    def run(self):
        self.current_time = time.time()
        TriggerWorkflow.run(self)

    def update_trigger(self):
        self.will_trigger = time.time() - self.current_time >= self.get_param("interval")
        if self.will_trigger:
            self.current_time = time.time()
            self.log(f"触发器触发，间隔: {self.get_param('interval')}s")