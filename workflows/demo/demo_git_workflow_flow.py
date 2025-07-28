# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
from workflows.git.git_status_flow import GitStatusFlow
from workflows.git.git_pull_flow import GitPullFlow
from workflows.git.git_commit_flow import GitCommitFlow
# from workflows.git.git_push_flow import GitPushFlow

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
        "commit_message": "自动提交更改",
        "add_all": True,
        "pull_before_commit": True,
        "push_after_commit": True,
        "check_status": True
    }
    
    def run(self):
        """执行Git工作流演示"""
        self.log("=" * 50)
        self.log("开始执行Git工作流演示")
        self.log("=" * 50)
        
        # 获取参数
        repo_path = self.get_param("repository_path")
        commit_message = self.get_param("commit_message")
        add_all = self.get_param("add_all")
        pull_before_commit = self.get_param("pull_before_commit")
        push_after_commit = self.get_param("push_after_commit")
        check_status = self.get_param("check_status")
        
        self.log(f"仓库路径: {repo_path}")
        self.log(f"提交信息: {commit_message}")
        self.log(f"添加所有文件: {add_all}")
        self.log(f"提交前拉取: {pull_before_commit}")
        self.log(f"提交后推送: {push_after_commit}")
        self.log(f"检查状态: {check_status}")
        
        results = {}
        
        # 1. 检查Git状态
        if check_status:
            self.log("\n" + "-" * 30)
            self.log("步骤1: 检查Git状态")
            self.log("-" * 30)
            
            status_result = self.run_flow(GitStatusFlow, {
                "repository_path": repo_path,
                "verbose": True
            })
            
            results["status_check"] = status_result
            if status_result and status_result.get("status") == "success":
                self.log("✓ Git状态检查成功")
            else:
                self.log("✗ Git状态检查失败")
        
        # 2. 拉取最新更新
        if pull_before_commit:
            self.log("\n" + "-" * 30)
            self.log("步骤2: 拉取最新更新")
            self.log("-" * 30)
            
            pull_result = self.run_flow(GitPullFlow, {
                "repository_path": repo_path,
                "quiet": False
            })
            
            results["pull"] = pull_result
            if pull_result and pull_result.get("status") == "success":
                self.log("✓ Git拉取成功")
            else:
                self.log("✗ Git拉取失败")
        
        # 3. 提交更改
        self.log("\n" + "-" * 30)
        self.log("步骤3: 提交更改")
        self.log("-" * 30)
        
        commit_result = self.run_flow(GitCommitFlow, {
            "repository_path": repo_path,
            "message": commit_message,
            "add_all": add_all,
            "quiet": False
        })
        
        results["commit"] = commit_result
        if commit_result and commit_result.get("status") == "success":
            self.log("✓ Git提交成功")
        else:
            self.log("✗ Git提交失败")
        
        # 4. 推送更改
        # if push_after_commit:
        #     self.log("\n" + "-" * 30)
        #     self.log("步骤4: 推送更改")
        #     self.log("-" * 30)
            
        #     push_result = self.run_flow(GitPushFlow, {
        #         "repository_path": repo_path,
        #         "quiet": False
        #     })
            
        #     results["push"] = push_result
        #     if push_result and push_result.get("status") == "success":
        #         self.log("✓ Git推送成功")
        #     else:
        #         self.log("✗ Git推送失败")
        
        # 5. 最终状态检查
        if check_status:
            self.log("\n" + "-" * 30)
            self.log("步骤5: 最终状态检查")
            self.log("-" * 30)
            
            final_status_result = self.run_flow(GitStatusFlow, {
                "repository_path": repo_path,
                "verbose": True
            })
            
            results["final_status"] = final_status_result
            if final_status_result and final_status_result.get("status") == "success":
                self.log("✓ 最终状态检查成功")
            else:
                self.log("✗ 最终状态检查失败")
        
        # 总结结果
        self.log("\n" + "=" * 50)
        self.log("Git工作流演示完成")
        self.log("=" * 50)
        
        success_count = sum(1 for result in results.values() 
                          if result and result.get("status") == "success")
        total_count = len(results)
        
        self.log(f"成功步骤: {success_count}/{total_count}")
        
        # 设置共享值
        self.set_shared_value("git_workflow_results", results)
        self.set_shared_value("git_workflow_success_rate", f"{success_count}/{total_count}")
        
        return {
            "status": "success" if success_count == total_count else "partial",
            "repository_path": repo_path,
            "results": results,
            "success_rate": f"{success_count}/{total_count}",
            "message": "Git工作流演示完成"
        } 