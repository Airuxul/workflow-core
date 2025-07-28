# -*- coding: utf-8 -*-

from workflows.git.base_git_flow import BaseGitFlow

class GitCommitFlow(BaseGitFlow):
    """
    Git提交操作工作流
    
    这个工作流用于：
    1. 提交工作区的更改
    2. 支持指定提交信息
    3. 支持添加所有文件
    4. 支持修改最后一次提交
    5. 记录提交结果
    """
    
    DEFAULT_PARAMS = {
        "repository_path": ".",
        "message": "",
        "add_all": False,
        "amend": False,
        "quiet": False,
        "allow_empty": False,
        "no_verify": False
    }
    
    def init(self):
        super().init()
        self.message = self.get_param("message")
        self.add_all = self.get_param("add_all")
        self.amend = self.get_param("amend")
        self.quiet = self.get_param("quiet")
        self.allow_empty = self.get_param("allow_empty")
        self.no_verify = self.get_param("no_verify")
    
    def execute_cmd(self):
        """执行Git提交操作"""
        self.log("=" * 40)
        self.log("开始执行Git提交操作")
        self.log("=" * 40)
        
        # 验证提交信息
        if not self.message and not self.amend:
            error_msg = "错误：必须提供提交信息或使用amend模式"
            self.log(error_msg)
            return {"status": "error", "message": error_msg}
        
        # 如果需要添加所有文件
        if self.add_all:
            self.log("添加所有文件到暂存区...")
            add_result = self._execute_git_cmd("add", ".")
            
            if not isinstance(add_result, dict) or add_result.get("status") != "success":
                error_msg = "添加文件到暂存区失败"
                self.log(error_msg)
                return {"status": "error", "message": error_msg}
        
        # 构建命令参数
        args = []
        if self.amend:
            args.append("--amend")
        if self.quiet:
            args.append("--quiet")
        if self.allow_empty:
            args.append("--allow-empty")
        if self.no_verify:
            args.append("--no-verify")
        if self.message and not self.amend:
            args.extend(["-m", f'"{self.message}"'])
        
        # 记录参数信息
        if self.message:
            self.log(f"提交信息: {self.message}")
        if self.add_all:
            self.log("已添加所有文件")
        if self.amend:
            self.log("修改最后一次提交")
        if self.allow_empty:
            self.log("允许空提交")
        if self.no_verify:
            self.log("跳过钩子验证")
        
        # 执行Git提交命令
        result = self._execute_git_cmd("commit", *args)
        
        # 如果成功，格式化返回结果
        if isinstance(result, dict) and result.get("status") == "success":
            return self._format_success_result(
                "commit",
                commit_message=self.message
            )
        
        return result 