# -*- coding: utf-8 -*-

from workflows.git.base_git_flow import BaseGitFlow
from core.constants import WorkflowStatus
from enum import Enum

# Git分支操作类型枚举
class GitBranchOperation(Enum):
    LIST = 'list'
    CHECK = 'check'
    CREATE = 'create'
    DELETE = 'delete'
    SWITCH = 'switch'  # 替换原来的checkout

class GitBranchFlow(BaseGitFlow):
    """
    Git分支工作流
    
    用于分支相关操作：列出分支、检查分支存在性、创建分支、删除分支等
    """
    
    DEFAULT_PARAMS = {
        "repository_path": ".",
        "operation": GitBranchOperation.LIST.value,  # 使用字符串，在init中会处理
        "branch_name": None,
        "remote": False,      # 是否检查远程分支
        "create_branch": False,  # 是否创建新分支
        "track_remote": False,   # 是否跟踪远程分支
        "remote_branch": None,   # 远程分支名
        "delete_branch": False,  # 是否删除分支
        "force": False,       # 强制操作
        "quiet": False
    }
    
    def init(self):
        super().init()
        self.operation = self.get_param("operation")
        self.branch_name = self.get_param("branch_name")
        self.remote = self.get_param("remote")
        self.create_branch = self.get_param("create_branch")
        self.track_remote = self.get_param("track_remote")
        self.remote_branch = self.get_param("remote_branch")
        self.delete_branch = self.get_param("delete_branch")
        self.force = self.get_param("force")
    
    def execute_cmd(self):
        """执行Git分支操作"""
        if self.operation == GitBranchOperation.LIST.value:
            return self._list_branches()
        elif self.operation == GitBranchOperation.CHECK.value:
            return self._check_branch()
        elif self.operation == GitBranchOperation.CREATE.value:
            return self._create_branch()
        elif self.operation == GitBranchOperation.DELETE.value:
            return self._delete_branch()
        elif self.operation == GitBranchOperation.SWITCH.value:
            return self._switch_branch()
        else:
            return {"status": WorkflowStatus.ERROR.value, "message": f"不支持的操作: {self.operation}"}
    
    def _list_branches(self):
        """列出分支"""
        if self.remote:
            git_args = ["branch", "-r", "--list"]
        else:
            git_args = ["branch", "--list"]
        if self.branch_name:
            git_args.append(self.branch_name)
        return self._execute_git_cmd(*git_args)
    
    def _check_branch(self):
        """检查分支是否存在"""
        if self.remote:
            git_args = ["branch", "-r", "--list", f"origin/{self.branch_name}"]
        else:
            git_args = ["branch", "--list", self.branch_name]
        return self._execute_git_cmd(*git_args)
    
    def _create_branch(self):
        """创建分支"""
        if self.track_remote and self.remote_branch:
            # 创建并切换到跟踪远程分支的本地分支
            git_args = ["switch", "-c", self.branch_name, self.remote_branch]
        else:
            # 创建新分支
            git_args = ["switch", "-c", self.branch_name]
        return self._execute_git_cmd(*git_args)
    
    def _delete_branch(self):
        """删除分支"""
        git_args = ["branch"]
        if self.force:
            git_args.append("-D")
        else:
            git_args.append("-d")
        git_args.append(self.branch_name)
        return self._execute_git_cmd(*git_args)
    
    def _switch_branch(self):
        """切换到分支"""
        git_args = ["switch", self.branch_name]
        return self._execute_git_cmd(*git_args) 