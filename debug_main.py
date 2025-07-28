# -*- coding: utf-8 -*-

from core.manager import WorkflowManager

# 调试配置
DEBUG_CONFIGS = {
    "trigger": {
        "flow": "test.test_interval_trigger_flow",
    },
    "shared_context": {
        "flow": "demo.demo_shared_context_flow",
    },
    "git_workflow": {
        "flow_data": "data/workflowData/demo/demo_git_flow_data.json",
    }
}

def debug_workflow(config_name: str):
    """调试指定的工作流"""
    if config_name in DEBUG_CONFIGS:
        WorkflowManager.run_workflow(DEBUG_CONFIGS[config_name])
    else:
        print(f"未知的调试配置: {config_name}")

if __name__ == "__main__":
    debug_workflow("git_workflow")