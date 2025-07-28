# -*- coding: utf-8 -*-

from workflows.git.base_git_flow import BaseGitFlow
import os

class GitCloneFlow(BaseGitFlow):
    """
    Git克隆操作工作流
    
    这个工作流用于：
    1. 克隆Git仓库到指定目录
    2. 支持指定分支
    3. 支持深度克隆
    4. 记录克隆结果
    """
    
    DEFAULT_PARAMS = {
        "repository_url": "",
        "target_directory": "",
        "branch": "main",
        "depth": None,
        "quiet": False
    }
    
    def init(self):
        super().init()
        self.repo_url = self.get_param("repository_url")
        self.target_dir = self.get_param("target_directory")
        self.branch = self.get_param("branch")
        self.depth = self.get_param("depth")
        self.quiet = self.get_param("quiet")
    
    def execute_cmd(self):
        """执行Git克隆操作"""
        self.log("=" * 40)
        self.log("开始执行Git克隆操作")
        self.log("=" * 40)
        
        # 验证必要参数
        if not self.repo_url:
            error_msg = "错误：必须提供repository_url参数"
            self.log(error_msg)
            return {"status": "error", "message": error_msg}
        
        if not self.target_dir:
            # 从URL中提取仓库名作为默认目录
            repo_name = self.repo_url.split('/')[-1].replace('.git', '')
            self.target_dir = repo_name
            self.log(f"未指定目标目录，使用默认目录: {self.target_dir}")
        
        # 构建命令参数
        args = []
        if self.branch and self.branch != "main":
            args.extend(["-b", self.branch])
        if self.depth:
            args.extend(["--depth", str(self.depth)])
        if self.quiet:
            args.append("--quiet")
        args.extend([self.repo_url, self.target_dir])
        
        # 记录参数信息
        self.log(f"仓库URL: {self.repo_url}")
        self.log(f"目标目录: {self.target_dir}")
        self.log(f"分支: {self.branch}")
        if self.depth:
            self.log(f"克隆深度: {self.depth}")
        
        # 检查目标目录是否已存在
        if os.path.exists(self.target_dir):
            self.log(f"警告：目标目录 {self.target_dir} 已存在")
        
        # 执行Git克隆命令
        git_cmd = " ".join(["git", "clone"] + args)
        result = self._execute_command(git_cmd)
        
        # 如果成功，格式化返回结果
        if isinstance(result, dict) and result.get("status") == "success":
            return self._format_success_result(
                "clone",
                repository_url=self.repo_url,
                target_directory=self.target_dir,
                branch=self.branch
            )
        
        return result 