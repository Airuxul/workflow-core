# -*- coding: utf-8 -*-

from workflows.base_workflow import BaseWorkflow
from workflows.git.git_switch_update_flow import GitSwitchUpdateFlow

class DemoGitSwitchUpdateFlow(BaseWorkflow):
    """
    Git分支切换和更新演示工作流
    
    这个演示工作流展示如何使用GitSwitchUpdateFlow来：
    1. 回退当前分支的修改（保留submodule）
    2. 切换到指定分支
    3. 更新到最新版本
    """
    
    DEFAULT_PARAMS = {
        "repository_path": ".",
        "target_branch": "main",
        "preserve_submodules": True,
        "update_after_switch": True,
        "show_detailed_logs": True
    }
    
    def init(self):
        self.repository_path = self.get_param("repository_path")
        self.target_branch = self.get_param("target_branch")
        self.preserve_submodules = self.get_param("preserve_submodules")
        self.update_after_switch = self.get_param("update_after_switch")
        self.show_detailed_logs = self.get_param("show_detailed_logs")
    
    def run(self):
        """执行Git分支切换和更新演示"""
        self.log("=" * 60)
        self.log("Git分支切换和更新演示")
        self.log("=" * 60)
        
        # 显示配置信息
        self.log("配置信息:")
        self.log(f"  仓库路径: {self.repository_path}")
        self.log(f"  目标分支: {self.target_branch}")
        self.log(f"  保留submodule: {self.preserve_submodules}")
        self.log(f"  切换后更新: {self.update_after_switch}")
        self.log(f"  详细日志: {self.show_detailed_logs}")
        self.log("")
        
        # 执行Git分支切换和更新操作
        self.log("开始执行Git分支切换和更新操作...")
        
        switch_update_params = {
            "repository_path": self.repository_path,
            "target_branch": self.target_branch,
            "preserve_submodules": self.preserve_submodules,
            "update_after_switch": self.update_after_switch,
            "quiet": not self.show_detailed_logs
        }
        
        result = self.run_flow(GitSwitchUpdateFlow, switch_update_params)
        
        # 处理结果
        if isinstance(result, dict):
            if result.get("status") == "success":
                self.log("")
                self.log("✅ Git分支切换和更新操作成功完成!")
                self.log("")
                self.log("操作结果:")
                self.log(f"  目标分支: {result.get('target_branch', 'N/A')}")
                self.log(f"  保留submodule: {result.get('preserved_submodules', 'N/A')}")
                self.log(f"  已更新: {result.get('updated', 'N/A')}")
                self.log(f"  操作类型: {result.get('operation', 'N/A')}")
                self.log(f"  消息: {result.get('message', 'N/A')}")
                
                # 显示额外的结果信息
                if "repository_path" in result:
                    self.log(f"  仓库路径: {result['repository_path']}")
                
                return {
                    "status": "success",
                    "message": "Git分支切换和更新演示成功完成",
                    "target_branch": result.get("target_branch"),
                    "preserved_submodules": result.get("preserved_submodules"),
                    "updated": result.get("updated")
                }
            else:
                self.log("")
                self.log("❌ Git分支切换和更新操作失败!")
                self.log(f"错误信息: {result.get('message', '未知错误')}")
                return result
        else:
            error_msg = "Git分支切换和更新操作返回了意外的结果类型"
            self.log(f"❌ {error_msg}")
            return {"status": "error", "message": error_msg} 