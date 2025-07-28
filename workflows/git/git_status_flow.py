# -*- coding: utf-8 -*-

from workflows.git.base_git_flow import BaseGitFlow

class GitStatusFlow(BaseGitFlow):
    """
    Git状态检查操作工作流
    
    这个工作流用于：
    1. 检查Git仓库状态
    2. 显示工作区和暂存区的状态
    3. 支持详细输出
    4. 记录状态信息
    """
    
    DEFAULT_PARAMS = {
        "repository_path": ".",
        "porcelain": False,
        "branch": False,
        "verbose": False,
        "ignore_submodules": False
    }
    
    def init(self):
        super().init()
        self.porcelain = self.get_param("porcelain")
        self.branch = self.get_param("branch")
        self.verbose = self.get_param("verbose")
        self.ignore_submodules = self.get_param("ignore_submodules")
    
    def execute_cmd(self):
        """执行Git状态检查"""
        # 构建命令参数
        args = []
        if self.porcelain:
            args.append("--porcelain")
        if self.branch:
            args.append("--branch")
        if self.verbose:
            args.append("--verbose")
        if self.ignore_submodules:
            args.append("--ignore-submodules")
        
        # 执行Git状态命令
        result = self._execute_git_cmd("status", *args)
        
        # 如果成功，格式化返回结果
        if isinstance(result, dict) and result.get("status") == "success":
            return self._format_success_result(
                "status",
                status_output=result.get("output", "")
            )
        
        return result 