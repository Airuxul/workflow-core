# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
from workflows.system.bat_flow import BatFlow
import os

class GitCloneFlow(BaseWorkflow):
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
    
    def run(self):
        """执行Git克隆操作"""
        self.log("=" * 40)
        self.log("开始执行Git克隆操作")
        self.log("=" * 40)
        
        # 获取参数
        repo_url = self.get_param("repository_url")
        target_dir = self.get_param("target_directory")
        branch = self.get_param("branch")
        depth = self.get_param("depth")
        quiet = self.get_param("quiet")
        
        # 验证必要参数
        if not repo_url:
            error_msg = "错误：必须提供repository_url参数"
            self.log(error_msg)
            return {"status": "error", "message": error_msg}
        
        if not target_dir:
            # 从URL中提取仓库名作为默认目录
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            target_dir = repo_name
            self.log(f"未指定目标目录，使用默认目录: {target_dir}")
        
        # 构建Git命令
        cmd_parts = ["git", "clone"]
        
        if branch and branch != "main":
            cmd_parts.extend(["-b", branch])
        
        if depth:
            cmd_parts.extend(["--depth", str(depth)])
        
        if quiet:
            cmd_parts.append("--quiet")
        
        cmd_parts.extend([repo_url, target_dir])
        
        git_cmd = " ".join(cmd_parts)
        
        self.log(f"仓库URL: {repo_url}")
        self.log(f"目标目录: {target_dir}")
        self.log(f"分支: {branch}")
        if depth:
            self.log(f"克隆深度: {depth}")
        self.log(f"执行命令: {git_cmd}")
        
        # 检查目标目录是否已存在
        if os.path.exists(target_dir):
            self.log(f"警告：目标目录 {target_dir} 已存在")
            self.set_shared_value("clone_warning", f"目标目录 {target_dir} 已存在")
        
        # 执行克隆操作
        try:
            result = self.run_flow(BatFlow, {
                "cmd": git_cmd,
                "wait": True
            })
            
            # 检查克隆结果
            if result and result.get("status") == "success":
                self.log("Git克隆操作成功完成")
                
                # 设置共享值
                self.set_shared_value("cloned_repository", repo_url)
                self.set_shared_value("cloned_directory", target_dir)
                self.set_shared_value("cloned_branch", branch)
                
                return {
                    "status": "success",
                    "repository_url": repo_url,
                    "target_directory": target_dir,
                    "branch": branch,
                    "message": "Git克隆操作成功完成"
                }
            else:
                error_msg = f"Git克隆操作失败: {result.get('message', '未知错误')}"
                self.log(error_msg)
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"Git克隆操作异常: {str(e)}"
            self.log(error_msg)
            return {"status": "error", "message": error_msg} 