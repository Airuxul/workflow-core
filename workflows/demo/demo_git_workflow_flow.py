# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
from core.constants import WorkflowStatus
from workflows.git.git_status_flow import GitStatusFlow

class DemoGitWorkflowFlow(BaseWorkflow):
    """
    Git工作流演示
    
    这个工作流演示了：
    1. 如何检查Git仓库状态
    2. 如何拉取最新更新
    3. 如何提交更改
    4. 如何推送更改
    5. 完整的Git工作流程
    """
    
    DEFAULT_PARAMS = {
        "repository_path": ".",
        "check_status": True
    }
    
    def run(self):
        """执行Git工作流演示"""
        self.log("=" * 50)
        self.log("开始执行Git工作流演示")
        self.log("=" * 50)
        
        # 获取参数
        repo_path = self.get_param("repository_path")
        check_status = self.get_param("check_status")
        
        self.log(f"仓库路径: {repo_path}")
        self.log(f"检查状态: {check_status}")
        self.log("-" * 30)
        self.log("步骤1: 检查Git状态")
        self.log("-" * 30)
        self.run_flow(GitStatusFlow, {
            "repository_path": repo_path,
            "verbose": True
        })
