# -*- coding: utf-8 -*-

import importlib
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
    根据流程名称动态导入模块并找到其中的工作流类。
    优化：支持 flow_name 到类名的自动转换，优先直接 getattr，找不到直接报错。
    """
    try:
        module_path = f"workflows.{flow_name.replace('-', '_')}"
        workflow_module = importlib.import_module(module_path)
        class_name = flow_name_to_class_name(flow_name)
        # 只尝试直接 getattr
        if hasattr(workflow_module, class_name):
            obj = getattr(workflow_module, class_name)
            if issubclass(obj, BaseWorkflow) and obj is not BaseWorkflow:
                return obj
        raise AttributeError(f"在 '{flow_name}.py' 中未找到类名为 '{class_name}' 的 BaseWorkflow 子类。")
    except ModuleNotFoundError:
        raise FileNotFoundError(f"找不到工作流文件 'workflows/{flow_name}.py'")

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

def run_workflow(params: dict):
    """
    启动指定工作流。只接收一个包含flow和参数的dict。
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

def safe_filename(name: str) -> str:
    """
    替换Windows文件名中的非法字符为空格。
    """
    import re
    return re.sub(r'[\\/*?:"<>|]', ' ', name)