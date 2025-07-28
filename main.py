# -*- coding: utf-8 -*-

from core.utils import Utils
from core.manager import WorkflowManager

if __name__ == "__main__":
    params = Utils.parse_cmd_args()
    WorkflowManager.run_workflow(params)