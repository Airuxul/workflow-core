# -*- coding: utf-8 -*-

from core.utils import run_workflow

def debug_main():
    # 直接在这里填写要调试的参数
    params = {
        "flow": "main_test_flow",
    }
    run_workflow(params)

def debug_trigger():
    params = {
        "flow": "test.test_interval_trigger_flow",
    }
    run_workflow(params)

if __name__ == "__main__":
    debug_trigger()