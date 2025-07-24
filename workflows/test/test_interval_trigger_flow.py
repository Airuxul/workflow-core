# -*- coding: utf-8 -*-
from core.workflow import BaseWorkflow
from workflows.trigger.interval_trigger_flow import IntervalTriggerWorkflow

class TestIntervalTriggerFlow(BaseWorkflow):
    """
    测试workflow：每隔10秒触发一次，触发时执行data/workflowData/test.json中的workflow。
    """
    DEFAULT_PARAMS = {
    }

    def run(self):
        self.run_flow(IntervalTriggerWorkflow, {"trigger_workflow_data": "data/workflowData/test.json"})
