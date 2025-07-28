# -*- coding: utf-8 -*-

from workflows.git.base_git_flow import BaseGitFlow

class GitPullFlow(BaseGitFlow):
    """
    Git拉取更新操作工作流
    
    这个工作流用于：
    1. 拉取远程仓库的最新更新
    2. 支持指定分支
    3. 支持静默模式
    4. 记录拉取结果
    """
    
    DEFAULT_PARAMS = {
        "repository_path": ".",
        "branch": None,
        "quiet": False,
        "rebase": False,
        "ff_only": False
    }
    
    def init(self):
        super().init()
        self.branch = self.get_param("branch")
        self.quiet = self.get_param("quiet")
        self.rebase = self.get_param("rebase")
        self.ff_only = self.get_param("ff_only")
    
    def execute_cmd(self):
        """执行Git拉取操作"""
        # 构建命令参数
        args = []
        if self.branch:
            args.extend(["origin", self.branch])
        if self.rebase:
            args.append("--rebase")
        if self.ff_only:
            args.append("--ff-only")
        if self.quiet:
            args.append("--quiet")
        
        # 执行Git拉取命令
        result = self._execute_git_cmd("pull", *args)
        
        # 如果成功，格式化返回结果
        if isinstance(result, dict) and result.get("status") == "success":
            return self._format_success_result(
                "pull",
                branch=self.branch
            )
        
        return result 