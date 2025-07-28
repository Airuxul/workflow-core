# -*- coding: utf-8 -*-

from workflows.system.bat_flow import BatFlow
import os

class BaseGitFlow(BatFlow):
    """
    Git操作的基础工作流类
    
    这个类继承自BatFlow，提供Git操作的通用功能：
    1. 仓库路径验证
    2. Git命令构建
    3. 结果格式化
    """
    
    DEFAULT_PARAMS = {
        "repository_path": ".",
        "quiet": False
    }
    
    def init(self):
        super().init()
        self.repo_path = self.get_param("repository_path")
        self.quiet = self.get_param("quiet")
    
    def _validate_repository(self, repo_path):
        """验证Git仓库路径"""
        if not os.path.exists(repo_path):
            error_msg = f"错误：仓库路径不存在: {repo_path}"
            self.log(error_msg)
            return False, {"status": "error", "message": error_msg}
        
        # 检查是否为Git仓库
        git_dir = os.path.join(repo_path, ".git")
        if not os.path.exists(git_dir):
            error_msg = f"错误：路径 {repo_path} 不是有效的Git仓库"
            self.log(error_msg)
            return False, {"status": "error", "message": error_msg}
        
        return True, None
    
    def _build_git_cmd(self, git_subcommand, *args):
        """构建Git命令"""
        cmd_parts = ["git", "-C", self.repo_path, git_subcommand]
        cmd_parts.extend(args)
        return " ".join(cmd_parts)
    
    def _execute_git_cmd(self, git_subcommand, *args):
        """执行Git命令"""
        # 验证仓库
        is_valid, error_result = self._validate_repository(self.repo_path)
        if not is_valid:
            return error_result
        
        # 构建并执行命令
        git_cmd = self._build_git_cmd(git_subcommand, *args)
        self.log(f"仓库路径: {self.repo_path}")
        self.log(f"执行命令: {git_cmd}")
        
        return self._execute_command(git_cmd)
    
    def _format_success_result(self, operation, **extra_data):
        """格式化成功结果"""
        result = {
            "status": "success",
            "repository_path": self.repo_path,
            "operation": operation,
            "message": f"Git {operation} 操作成功完成"
        }
        result.update(extra_data)
        return result 