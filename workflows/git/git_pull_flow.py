# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
from workflows.system.bat_flow import BatFlow
import os

class GitPullFlow(BaseWorkflow):
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
    
    def run(self):
        """执行Git拉取操作"""
        self.log("=" * 40)
        self.log("开始执行Git拉取操作")
        self.log("=" * 40)
        
        # 获取参数
        repo_path = self.get_param("repository_path")
        branch = self.get_param("branch")
        quiet = self.get_param("quiet")
        rebase = self.get_param("rebase")
        ff_only = self.get_param("ff_only")
        
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
        cmd_parts = ["git", "-C", repo_path, "pull"]
        
        if branch:
            cmd_parts.extend(["origin", branch])
        
        if rebase:
            cmd_parts.append("--rebase")
        
        if ff_only:
            cmd_parts.append("--ff-only")
        
        if quiet:
            cmd_parts.append("--quiet")
        
        git_cmd = " ".join(cmd_parts)
        
        self.log(f"仓库路径: {repo_path}")
        if branch:
            self.log(f"目标分支: {branch}")
        if rebase:
            self.log("使用rebase模式")
        if ff_only:
            self.log("仅允许快进合并")
        self.log(f"执行命令: {git_cmd}")
        
        # 执行拉取操作
        try:
            result = self.run_flow(BatFlow, {
                "cmd": git_cmd,
                "wait": True
            })
            
            # 检查拉取结果
            if result and result.get("status") == "success":
                self.log("Git拉取操作成功完成")
                
                # 设置共享值
                self.set_shared_value("pulled_repository", repo_path)
                if branch:
                    self.set_shared_value("pulled_branch", branch)
                
                return {
                    "status": "success",
                    "repository_path": repo_path,
                    "branch": branch,
                    "message": "Git拉取操作成功完成"
                }
            else:
                error_msg = f"Git拉取操作失败: {result.get('message', '未知错误')}"
                self.log(error_msg)
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"Git拉取操作异常: {str(e)}"
            self.log(error_msg)
            return {"status": "error", "message": error_msg} 