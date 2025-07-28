# -*- coding: utf-8 -*-

from workflows.git.base_git_flow import BaseGitFlow

class GitResetFlow(BaseGitFlow):
    """
    Git重置工作流
    
    用于重置Git仓库的工作区和暂存区到指定状态
    """
    
    DEFAULT_PARAMS = {
        "repository_path": ".",
        "reset_type": "hard",  # hard, soft, mixed
        "target": "HEAD",      # HEAD, commit_hash, branch_name
        "quiet": False
    }
    
    def init(self):
        super().init()
        self.reset_type = self.get_param("reset_type")
        self.target = self.get_param("target")
    
    def execute_cmd(self):
        """执行Git重置操作"""
        git_args = ["reset", f"--{self.reset_type}", self.target]
        return self._execute_git_cmd(*git_args) 