# -*- coding: utf-8 -*-

from workflows.git.base_git_flow import BaseGitFlow

class GitFetchFlow(BaseGitFlow):
    """
    Git获取远程更新工作流
    
    用于从远程仓库获取更新
    """
    
    DEFAULT_PARAMS = {
        "repository_path": ".",
        "remote": "origin",  # 远程仓库名
        "all": False,        # 是否获取所有远程
        "quiet": False
    }
    
    def init(self):
        super().init()
        self.remote = self.get_param("remote")
        self.all = self.get_param("all")
    
    def execute_cmd(self):
        """执行Git获取远程更新操作"""
        if self.all:
            git_args = ["fetch", "--all"]
        else:
            git_args = ["fetch", self.remote]
        
        return self._execute_git_cmd(*git_args) 