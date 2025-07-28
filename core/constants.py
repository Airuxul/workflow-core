# -*- coding: utf-8 -*-

"""
项目使用的所有常量
"""

from enum import Enum

# 工作流日志格式
LOG_FLOW_START_FORMAT = "[工作流开始]: {name}"
LOG_FLOW_END_FORMAT = "[工作流结束]: {name}"

class LogTreePreType(Enum):
    START = 'start'
    MID = 'mid'
    END = 'end'

LOG_FLOW_START_TREE = "┏━"
LOG_FLOW_MID_TREE = "┣━" 
LOG_FLOW_END_TREE = "┗━"

LOG_TREE_INDENT = '  '  # 每层缩进2个空格

# 工作流执行状态常量
class WorkflowStatus(Enum):
    SUCCESS = 'success'
    ERROR = 'error'
    ASYNC = 'async'
    PARTIAL = 'partial'

# 状态消息常量
WORKFLOW_STATUS_MESSAGES = {
    WorkflowStatus.SUCCESS: "执行成功",
    WorkflowStatus.ERROR: "执行失败",
    WorkflowStatus.ASYNC: "异步执行中",
    WorkflowStatus.PARTIAL: "部分成功"
}
