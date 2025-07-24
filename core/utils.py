# -*- coding: utf-8 -*-

import importlib
import json
from typing import List
from core.logger import WorkflowLogger
from core.workflow import BaseWorkflow

def flow_name_to_class_name(flow_name: str) -> str:
    """
    将 flow_name（如 main_test_flow）转换为类名（如 MainTestFlow）。
    如果已经以 Flow 结尾，不再重复加。
    """
    class_name = ''.join(word.capitalize() for word in flow_name.replace('-', '_').split('_'))
    return class_name

def find_workflow_class(flow_name: str):
    """
    支持目录.文件（如 demo.async_test_flow）格式，精确查找对应workflow类。
    """
    if '.' not in flow_name:
        raise ValueError("flow_name 必须为 '目录.文件' 格式，如 demo.main_test_flow")
    module_path = f"workflows.{flow_name.replace('-', '_')}"
    workflow_module = importlib.import_module(module_path)
    class_name = flow_name_to_class_name(flow_name.split('.')[-1])
    if hasattr(workflow_module, class_name):
        obj = getattr(workflow_module, class_name)
        if issubclass(obj, BaseWorkflow) and obj is not BaseWorkflow:
            return obj
    raise AttributeError(f"在 '{flow_name}.py' 中未找到类名为 '{class_name}' 的 BaseWorkflow 子类。")

def parse_extra_args(extra_args: List[str]) -> dict:
    """
    将 ['--key1', 'value1', '--key2', 'value2'] 格式的列表解析为字典。
    """
    params = {}
    for i in range(0, len(extra_args), 2):
        key_with_dashes = extra_args[i]
        if key_with_dashes.startswith('--'):
            key = key_with_dashes[2:]
            if i + 1 < len(extra_args):
                params[key] = extra_args[i+1]
    return params

def parse_cmd_args():
    """
    解析命令行所有 --key value 参数为 dict。
    """
    import argparse
    parser = argparse.ArgumentParser(description="工作流执行引擎")
    _, unknown = parser.parse_known_args()
    params = {}
    for i in range(0, len(unknown), 2):
        key = unknown[i].lstrip('-')
        if i + 1 < len(unknown):
            params[key] = unknown[i+1]
    return params

def run_workflow_from_json(json_path: str):
    """
    从json文件读取参数并执行工作流。
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        params = json.load(f)
    run_workflow_from_dict(params)

def run_workflow_from_dict(params: dict):
    """
    直接用dict参数执行工作流。
    """
    from core.manager import WorkflowManager
    flow_name = params.get('flow', None)
    if not flow_name:
        WorkflowLogger.instance().error("参数必须包含'flow'字段，且为工作流名称！")
        return
    cli_params = {k: v for k, v in params.items() if k != 'flow'}
    try:
        main_workflow_class = find_workflow_class(flow_name)
        manager = WorkflowManager(cli_params=cli_params)
        manager.run_flow(workflow_class=main_workflow_class)
    except (FileNotFoundError, AttributeError) as e:
        WorkflowLogger.instance().error(f"错误: {e}")
    except Exception as e:
        WorkflowLogger.instance().error(f"发生致命错误: {e}")
        import traceback
        traceback.print_exc()

def run_workflow(params: dict):
    """
    工作流主入口。支持传入dict或通过workflow_data字段指定json文件。
    """
    workflow_data = params.get('workflow_data', None)
    if workflow_data:
        run_workflow_from_json(workflow_data)
    else:
        run_workflow_from_dict(params)

def safe_filename(name: str) -> str:
    """
    替换Windows文件名中的非法字符为空格。
    """
    import re
    return re.sub(r'[\\/*?:"<>|]', ' ', name)