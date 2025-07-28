# -*- coding: utf-8 -*-

from core.utils import run_workflow

def debug_trigger():
    params = {
        "flow": "test.test_interval_trigger_flow",
    }
    run_workflow(params)

def debug_shared_context():
    params = {
        "flow": "demo.demo_shared_context_flow",
    }
    run_workflow(params)

def debug_git_workflow():
    params = {
        "flow_data": "data/workflowData/demo/demo_git_flow_data.json",
    }
    run_workflow(params)

if __name__ == "__main__":
    debug_git_workflow()