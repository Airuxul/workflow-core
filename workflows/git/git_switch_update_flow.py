# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
from core.constants import WorkflowStatus
from workflows.git.git_status_flow import GitStatusFlow
from workflows.git.git_reset_flow import GitResetFlow
from workflows.git.git_branch_flow import GitBranchFlow, GitBranchOperation
from workflows.git.git_fetch_flow import GitFetchFlow

class GitSwitchUpdateFlow(BaseWorkflow):
    """
    Git分支切换和更新组合工作流
    
    这个工作流用于：
    1. 回退当前分支的修改（保留submodule修改）
    2. 切换到指定分支
    3. 更新到最新版本
    4. 记录操作结果
    """
    
    DEFAULT_PARAMS = {
        "repository_path": ".",
        "target_branch": "main",
        "preserve_submodules": True,
        "update_after_switch": True,
        "quiet": False
    }
    
    def init(self):
        self.repository_path = self.get_param("repository_path")
        self.target_branch = self.get_param("target_branch")
        self.preserve_submodules = self.get_param("preserve_submodules")
        self.update_after_switch = self.get_param("update_after_switch")
        self.quiet = self.get_param("quiet")
    
    def run(self):
        """执行Git分支切换和更新操作"""
        self.log("=" * 50)
        self.log("开始执行Git分支切换和更新操作")
        self.log("=" * 50)
        
        # 步骤1: 检查当前状态
        self.log("步骤1: 检查当前Git状态")
        status_result = self._check_current_status()
        if not self._is_success(status_result):
            self.log("错误：无法获取Git状态")
            return status_result
        
        # 步骤2: 回退当前修改（保留submodule）
        self.log("步骤2: 回退当前分支修改")
        reset_result = self._reset_current_changes()
        if not self._is_success(reset_result):
            return reset_result
        
        # 步骤3: 切换到目标分支
        self.log("步骤3: 切换到目标分支")
        switch_result = self._switch_to_target_branch()
        if not self._is_success(switch_result):
            return switch_result
        
        # 步骤4: 更新到最新（如果需要）
        if self.update_after_switch:
            self.log("步骤4: 更新到最新版本")
            update_result = self._update_to_latest()
            if not self._is_success(update_result):
                return update_result
        
        # 返回成功结果
        return {
            "status": WorkflowStatus.SUCCESS.value,
            "message": "Git分支切换和更新操作成功完成",
            "operation": "switch_update",
            "target_branch": self.target_branch,
            "preserved_submodules": self.preserve_submodules,
            "updated": self.update_after_switch,
            "repository_path": self.repository_path
        }
    
    def _is_success(self, result):
        """检查操作是否成功"""
        return isinstance(result, dict) and result.get("status") == WorkflowStatus.SUCCESS.value
    
    def _handle_operation(self, operation_name, operation_func, *args, **kwargs):
        """通用操作处理接口"""
        try:
            result = operation_func(*args, **kwargs)
            return result
        except Exception as e:
            return {"status": WorkflowStatus.ERROR.value, "message": f"{operation_name}异常: {str(e)}"}
    
    def _check_current_status(self):
        """检查当前Git状态"""
        status_params = {
            "repository_path": self.repository_path,
            "quiet": self.quiet
        }
        
        return self._handle_operation("状态检查", self.run_flow, GitStatusFlow, status_params)
    
    def _reset_current_changes(self):
        """回退当前分支的修改"""
        self.log(f"回退当前分支修改，保留submodule: {self.preserve_submodules}")
        
        # 获取当前状态
        status_result = self._check_current_status()
        if not self._is_success(status_result):
            return status_result
        
        status_output = status_result.get("output", "")
        if not status_output or not status_output.strip():
            self.log("当前工作区干净，无需回退")
            return {"status": WorkflowStatus.SUCCESS.value, "message": "工作区已干净"}
        
        # 分析状态输出，识别submodule修改
        lines = status_output.strip().split('\n')
        other_changes = []
        
        for line in lines:
            if line.strip():
                # 检查是否为submodule相关修改
                if not self.preserve_submodules or not self._is_submodule_change(line):
                    other_changes.append(line)
        
        # 记录修改信息
        if other_changes:
            self.log(f"发现 {len(other_changes)} 个非submodule修改")
            for change in other_changes:
                self.log(f"  - {change}")
        
        # 执行回退操作 - 只回退非submodule的修改
        if other_changes:
            # 使用GitResetFlow执行重置操作
            reset_params = {
                "repository_path": self.repository_path,
                "reset_type": "hard",
                "target": "HEAD",
                "quiet": self.quiet
            }
            
            reset_result = self._handle_operation("重置操作", self.run_flow, GitResetFlow, reset_params)
            if not self._is_success(reset_result):
                return reset_result
            
            self.log("已回退所有非submodule修改")
        
        return {"status": WorkflowStatus.SUCCESS.value, "message": "回退操作完成"}
    
    def _is_submodule_change(self, status_line):
        """判断是否为submodule相关修改"""
        # Git状态格式: XY PATH
        # 对于submodule，通常包含.gitmodules或submodule路径
        parts = status_line.split()
        if len(parts) >= 2:
            path = parts[1]
            return (path == ".gitmodules" or 
                   path.endswith("/.git") or 
                   "submodule" in path.lower())
        return False
    
    def _switch_to_target_branch(self):
        """切换到目标分支"""
        self.log(f"切换到分支: {self.target_branch}")
        
        # 检查目标分支是否存在
        branch_check_params = {
            "repository_path": self.repository_path,
            "operation": GitBranchOperation.CHECK.value,
            "branch_name": self.target_branch,
            "remote": False,
            "quiet": self.quiet
        }
        
        branch_check = self._handle_operation("分支检查", self.run_flow, GitBranchFlow, branch_check_params)
        if not self._is_success(branch_check):
            return branch_check
        
        branch_output = branch_check.get("output", "")
        branch_exists = self.target_branch in branch_output
        
        if branch_exists:
            # 本地分支存在，直接切换
            self.log(f"本地分支 {self.target_branch} 存在，直接切换")
            checkout_params = {
                "repository_path": self.repository_path,
                "operation": GitBranchOperation.SWITCH.value,
                "branch_name": self.target_branch,
                "quiet": self.quiet
            }
        else:
            # 本地分支不存在，检查远程分支
            self.log(f"本地分支 {self.target_branch} 不存在，检查远程分支")
            remote_check_params = {
                "repository_path": self.repository_path,
                "operation": GitBranchOperation.CHECK.value,
                "branch_name": self.target_branch,
                "remote": True,
                "quiet": self.quiet
            }
            
            remote_check = self._handle_operation("远程分支检查", self.run_flow, GitBranchFlow, remote_check_params)
            if not self._is_success(remote_check):
                return remote_check
            
            remote_output = remote_check.get("output", "")
            remote_exists = f"origin/{self.target_branch}" in remote_output
            
            if remote_exists:
                self.log(f"目标分支 {self.target_branch} 在远程存在，创建本地分支")
                # 创建并切换到远程分支
                checkout_params = {
                    "repository_path": self.repository_path,
                    "operation": GitBranchOperation.CREATE.value,
                    "branch_name": self.target_branch,
                    "create_branch": True,
                    "track_remote": True,
                    "remote_branch": f"origin/{self.target_branch}",
                    "quiet": self.quiet
                }
            else:
                error_msg = f"错误：分支 {self.target_branch} 不存在"
                self.log(error_msg)
                return {"status": WorkflowStatus.ERROR.value, "message": error_msg}
        
        checkout_result = self._handle_operation("分支切换", self.run_flow, GitBranchFlow, checkout_params)
        if not self._is_success(checkout_result):
            return checkout_result
        
        self.log(f"成功切换到分支: {self.target_branch}")
        return {"status": WorkflowStatus.SUCCESS.value, "message": f"已切换到分支 {self.target_branch}"}
    
    def _update_to_latest(self):
        """更新到最新版本"""
        self.log("更新到最新版本")
        
        # 获取远程更新
        fetch_params = {
            "repository_path": self.repository_path,
            "remote": "origin",
            "all": False,
            "quiet": self.quiet
        }
        
        fetch_result = self._handle_operation("获取远程更新", self.run_flow, GitFetchFlow, fetch_params)
        if not self._is_success(fetch_result):
            return fetch_result
        
        # 重置到远程分支
        reset_params = {
            "repository_path": self.repository_path,
            "reset_type": "hard",
            "target": f"origin/{self.target_branch}",
            "quiet": self.quiet
        }
        
        reset_result = self._handle_operation("重置到远程分支", self.run_flow, GitResetFlow, reset_params)
        if not self._is_success(reset_result):
            return reset_result
        
        self.log("已更新到最新版本")
        return {"status": WorkflowStatus.SUCCESS.value, "message": "更新完成"} 