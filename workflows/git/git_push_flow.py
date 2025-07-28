# -*- coding: utf-8 -*-

from workflows.git.base_git_flow import BaseGitFlow

class GitPushFlow(BaseGitFlow):
    """
    Git推送操作工作流
    
    这个工作流用于：
    1. 推送本地提交到远程仓库
    2. 支持指定分支
    3. 支持强制推送
    4. 支持设置上游分支
    5. 记录推送结果
    """
    
    DEFAULT_PARAMS = {
        "repository_path": ".",
        "branch": None,
        "remote": "origin",
        "force": False,
        "set_upstream": False,
        "quiet": False
    }
    
    def init(self):
        super().init()
        self.branch = self.get_param("branch")
        self.remote = self.get_param("remote")
        self.force = self.get_param("force")
        self.set_upstream = self.get_param("set_upstream")
        self.quiet = self.get_param("quiet")
    
    def execute_cmd(self):
        """执行Git推送操作"""
        self.log("=" * 40)
        self.log("开始执行Git推送操作")
        self.log("=" * 40)
        
        # 构建命令参数
        args = []
        if self.force:
            args.append("--force")
        if self.set_upstream:
            args.append("--set-upstream")
        if self.quiet:
            args.append("--quiet")
        
        # 添加远程和分支
        if self.branch:
            args.extend([self.remote, self.branch])
        else:
            args.append(self.remote)
        
        # 记录参数信息
        self.log(f"远程仓库: {self.remote}")
        if self.branch:
            self.log(f"目标分支: {self.branch}")
        if self.force:
            self.log("使用强制推送")
        if self.set_upstream:
            self.log("设置上游分支")
        
        # 执行Git推送命令
        result = self._execute_git_cmd("push", *args)
        
        # 如果成功，格式化返回结果
        if isinstance(result, dict) and result.get("status") == "success":
            return self._format_success_result(
                "push",
                remote=self.remote,
                branch=self.branch
            )
        
        return result 