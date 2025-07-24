# -*- coding: utf-8 -*-
from core.workflow import BaseWorkflow
from core.utils import run_workflow_from_json

class TestWorkflowDataFlow(BaseWorkflow):
    """
    测试workflow：读取并执行data/workflowData/test.json中的workflow。
    """
    DEFAULT_PARAMS = {
        "workflow_data": "data/workflowData/test.json"
    }

    def run(self):
        workflow_data = self.get_param("workflow_data")
        self.log(f"开始执行json工作流: {workflow_data}")
        run_workflow_from_json(workflow_data)
        self.log("json工作流执行完毕") 