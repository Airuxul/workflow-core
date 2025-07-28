# -*- coding: utf-8 -*-

from workflows.base_workflow import BaseWorkflow
from workflows.git.git_switch_update_flow import GitSwitchUpdateFlow

class TestGitSwitchUpdateFlow(BaseWorkflow):
    """
    Git分支切换和更新工作流测试
    
    这个测试工作流用于验证GitSwitchUpdateFlow的功能：
    1. 测试参数验证
    2. 测试分支切换逻辑
    3. 测试submodule保留功能
    4. 测试错误处理
    """
    
    DEFAULT_PARAMS = {
        "repository_path": ".",
        "test_scenarios": [
            "basic_switch",
            "submodule_preserve",
            "error_handling"
        ],
        "target_branch": "main",
        "preserve_submodules": True,
        "update_after_switch": True
    }
    
    def init(self):
        self.repository_path = self.get_param("repository_path")
        self.test_scenarios = self.get_param("test_scenarios")
        self.target_branch = self.get_param("target_branch")
        self.preserve_submodules = self.get_param("preserve_submodules")
        self.update_after_switch = self.get_param("update_after_switch")
    
    def run(self):
        """执行Git分支切换和更新测试"""
        self.log("=" * 60)
        self.log("Git分支切换和更新工作流测试")
        self.log("=" * 60)
        
        test_results = []
        
        for scenario in self.test_scenarios:
            self.log(f"")
            self.log(f"测试场景: {scenario}")
            self.log("-" * 40)
            
            result = self._test_scenario(scenario)
            test_results.append({
                "scenario": scenario,
                "result": result
            })
            
            if isinstance(result, dict) and result.get("status") == "success":
                self.log(f"✅ 场景 {scenario} 测试通过")
            else:
                self.log(f"❌ 场景 {scenario} 测试失败")
        
        # 生成测试报告
        self.log("")
        self.log("=" * 60)
        self.log("测试报告")
        self.log("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_result in test_results:
            scenario = test_result["scenario"]
            result = test_result["result"]
            
            if isinstance(result, dict) and result.get("status") == "success":
                passed_tests += 1
                self.log(f"✅ {scenario}: 通过")
            else:
                error_msg = result.get("message", "未知错误") if isinstance(result, dict) else str(result)
                self.log(f"❌ {scenario}: 失败 - {error_msg}")
        
        self.log("")
        self.log(f"测试总结: {passed_tests}/{total_tests} 通过")
        
        if passed_tests == total_tests:
            return {
                "status": "success",
                "message": f"所有测试通过 ({passed_tests}/{total_tests})",
                "test_results": test_results
            }
        else:
            return {
                "status": "error",
                "message": f"部分测试失败 ({passed_tests}/{total_tests})",
                "test_results": test_results
            }
    
    def _test_scenario(self, scenario):
        """测试特定场景"""
        if scenario == "basic_switch":
            return self._test_basic_switch()
        elif scenario == "submodule_preserve":
            return self._test_submodule_preserve()
        elif scenario == "error_handling":
            return self._test_error_handling()
        else:
            return {"status": "error", "message": f"未知测试场景: {scenario}"}
    
    def _test_basic_switch(self):
        """测试基本分支切换功能"""
        self.log("测试基本分支切换功能...")
        
        # 使用基本参数测试
        params = {
            "repository_path": self.repository_path,
            "target_branch": self.target_branch,
            "preserve_submodules": False,  # 简化测试
            "update_after_switch": False,  # 简化测试
            "quiet": True
        }
        
        try:
            result = self.run_flow(GitSwitchUpdateFlow, params)
            return result
        except Exception as e:
            return {"status": "error", "message": f"基本切换测试异常: {str(e)}"}
    
    def _test_submodule_preserve(self):
        """测试submodule保留功能"""
        self.log("测试submodule保留功能...")
        
        # 使用submodule保留参数测试
        params = {
            "repository_path": self.repository_path,
            "target_branch": self.target_branch,
            "preserve_submodules": True,
            "update_after_switch": False,  # 简化测试
            "quiet": True
        }
        
        try:
            result = self.run_flow(GitSwitchUpdateFlow, params)
            return result
        except Exception as e:
            return {"status": "error", "message": f"Submodule保留测试异常: {str(e)}"}
    
    def _test_error_handling(self):
        """测试错误处理功能"""
        self.log("测试错误处理功能...")
        
        # 使用不存在的分支测试错误处理
        params = {
            "repository_path": self.repository_path,
            "target_branch": "non_existent_branch_12345",
            "preserve_submodules": True,
            "update_after_switch": False,
            "quiet": True
        }
        
        try:
            result = self.run_flow(GitSwitchUpdateFlow, params)
            
            # 期望返回错误状态
            if isinstance(result, dict) and result.get("status") == "error":
                return {"status": "success", "message": "错误处理测试通过"}
            else:
                return {"status": "error", "message": "错误处理测试失败：期望错误状态但得到成功"}
        except Exception as e:
            return {"status": "error", "message": f"错误处理测试异常: {str(e)}"} 