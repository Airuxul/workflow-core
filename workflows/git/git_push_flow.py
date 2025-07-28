# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
from workflows.system.bat_flow import BatFlow
import os

class GitPushFlow(BaseWorkflow):
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
    
    def run(self):
        """执行Git推送操作"""
        self.log("=" * 40)
        self.log("开始执行Git推送操作")
        self.log("=" * 40)
        
        # 获取参数
        repo_path = self.get_param("repository_path")
        branch = self.get_param("branch")
        remote = self.get_param("remote")
        force = self.get_param("force")
        set_upstream = self.get_param("set_upstream")
        quiet = self.get_param("quiet")
        
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
        cmd_parts = ["git", "-C", repo_path, "push"]
        
        if force:
            cmd_parts.append("--force")
        
        if set_upstream:
            cmd_parts.append("--set-upstream")
        
        if quiet:
            cmd_parts.append("--quiet")
        
        # 添加远程和分支
        if branch:
            cmd_parts.extend([remote, branch])
        else:
            cmd_parts.append(remote)
        
        git_cmd = " ".join(cmd_parts)
        
        self.log(f"仓库路径: {repo_path}")
        self.log(f"远程仓库: {remote}")
        if branch:
            self.log(f"目标分支: {branch}")
        if force:
            self.log("使用强制推送")
        if set_upstream:
            self.log("设置上游分支")
        self.log(f"执行命令: {git_cmd}")
        
        # 执行推送操作
        try:
            result = self.run_flow(BatFlow, {
                "cmd": git_cmd,
                "wait": True
            })
            
            # 检查推送结果
            if result and result.get("status") == "success":
                self.log("Git推送操作成功完成")
                
                # 设置共享值
                self.set_shared_value("pushed_repository", repo_path)
                self.set_shared_value("pushed_remote", remote)
                if branch:
                    self.set_shared_value("pushed_branch", branch)
                
                return {
                    "status": "success",
                    "repository_path": repo_path,
                    "remote": remote,
                    "branch": branch,
                    "message": "Git推送操作成功完成"
                }
            else:
                error_msg = f"Git推送操作失败: {result.get('message', '未知错误')}"
                self.log(error_msg)
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"Git推送操作异常: {str(e)}"
            self.log(error_msg)
            return {"status": "error", "message": error_msg} 