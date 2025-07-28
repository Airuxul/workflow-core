# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
from workflows.system.bat_flow import BatFlow
import os

class GitStatusFlow(BaseWorkflow):
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
    
    def run(self):
        """执行Git状态检查"""
        self.log("=" * 40)
        self.log("开始执行Git状态检查")
        self.log("=" * 40)
        
        # 获取参数
        repo_path = self.get_param("repository_path")
        porcelain = self.get_param("porcelain")
        branch = self.get_param("branch")
        verbose = self.get_param("verbose")
        ignore_submodules = self.get_param("ignore_submodules")
        
        # 验证仓库路径
        if not os.path.exists(repo_path):
            error_msg = f"错误：仓库路径不存在: {repo_path}"
            self.log(error_msg)
            return {"status": "error", "message": error_msg}
        
        # 检查是否为Git仓库
        git_dir = os.path.join(repo_path, ".git")
        if not os.path.exists(git_dir):
            error_msg = f"错误：路径 {repo_path} 不是有效的Git仓库"
            self.log(error_msg)
            return {"status": "error", "message": error_msg}
        
        # 构建Git命令
        cmd_parts = ["git", "-C", repo_path, "status"]
        
        if porcelain:
            cmd_parts.append("--porcelain")
        
        if branch:
            cmd_parts.append("--branch")
        
        if verbose:
            cmd_parts.append("--verbose")
        
        if ignore_submodules:
            cmd_parts.append("--ignore-submodules")
        
        git_cmd = " ".join(cmd_parts)
        
        self.log(f"仓库路径: {repo_path}")
        if porcelain:
            self.log("使用porcelain格式输出")
        if branch:
            self.log("显示分支信息")
        if verbose:
            self.log("使用详细输出")
        if ignore_submodules:
            self.log("忽略子模块")
        self.log(f"执行命令: {git_cmd}")
        
        # 执行状态检查
        try:
            result = self.run_flow(BatFlow, {
                "cmd": git_cmd,
                "wait": True
            })
            
            # 检查状态检查结果
            if result and result.get("status") == "success":
                self.log("Git状态检查成功完成")
                
                # 设置共享值
                self.set_shared_value("status_repository", repo_path)
                self.set_shared_value("status_result", result.get("output", ""))
                
                return {
                    "status": "success",
                    "repository_path": repo_path,
                    "status_output": result.get("output", ""),
                    "message": "Git状态检查成功完成"
                }
            else:
                error_msg = f"Git状态检查失败: {result.get('message', '未知错误')}"
                self.log(error_msg)
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"Git状态检查异常: {str(e)}"
            self.log(error_msg)
            return {"status": "error", "message": error_msg} 