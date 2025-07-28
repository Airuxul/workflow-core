# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
from workflows.system.bat_flow import BatFlow
import os

class GitCommitFlow(BaseWorkflow):
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
    
    def run(self):
        """执行Git提交操作"""
        self.log("=" * 40)
        self.log("开始执行Git提交操作")
        self.log("=" * 40)
        
        # 获取参数
        repo_path = self.get_param("repository_path")
        message = self.get_param("message")
        add_all = self.get_param("add_all")
        amend = self.get_param("amend")
        quiet = self.get_param("quiet")
        allow_empty = self.get_param("allow_empty")
        no_verify = self.get_param("no_verify")
        
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
        
        # 验证提交信息
        if not message and not amend:
            error_msg = "错误：必须提供提交信息或使用amend模式"
            self.log(error_msg)
            return {"status": "error", "message": error_msg}
        
        # 如果需要添加所有文件
        if add_all:
            self.log("添加所有文件到暂存区...")
            add_result = self.run_flow(BatFlow, {
                "cmd": f"git -C {repo_path} add .",
                "wait": True
            })
            
            if not add_result or add_result.get("status") != "success":
                error_msg = "添加文件到暂存区失败"
                self.log(error_msg)
                return {"status": "error", "message": error_msg}
        
        # 构建Git提交命令
        cmd_parts = ["git", "-C", repo_path, "commit"]
        
        if amend:
            cmd_parts.append("--amend")
        
        if quiet:
            cmd_parts.append("--quiet")
        
        if allow_empty:
            cmd_parts.append("--allow-empty")
        
        if no_verify:
            cmd_parts.append("--no-verify")
        
        if message and not amend:
            cmd_parts.extend(["-m", f'"{message}"'])
        
        git_cmd = " ".join(cmd_parts)
        
        self.log(f"仓库路径: {repo_path}")
        if message:
            self.log(f"提交信息: {message}")
        if add_all:
            self.log("已添加所有文件")
        if amend:
            self.log("修改最后一次提交")
        if allow_empty:
            self.log("允许空提交")
        if no_verify:
            self.log("跳过钩子验证")
        self.log(f"执行命令: {git_cmd}")
        
        # 执行提交操作
        try:
            result = self.run_flow(BatFlow, {
                "cmd": git_cmd,
                "wait": True
            })
            
            # 检查提交结果
            if result and result.get("status") == "success":
                self.log("Git提交操作成功完成")
                
                # 设置共享值
                self.set_shared_value("committed_repository", repo_path)
                if message:
                    self.set_shared_value("commit_message", message)
                
                return {
                    "status": "success",
                    "repository_path": repo_path,
                    "commit_message": message,
                    "message": "Git提交操作成功完成"
                }
            else:
                error_msg = f"Git提交操作失败: {result.get('message', '未知错误')}"
                self.log(error_msg)
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"Git提交操作异常: {str(e)}"
            self.log(error_msg)
            return {"status": "error", "message": error_msg} 