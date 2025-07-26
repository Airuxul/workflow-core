# -*- coding: utf-8 -*-
from core.workflow import BaseWorkflow

class DemoNestFlow(BaseWorkflow):
    """
    四层嵌套演示工作流（仅暴露此类，内部包含所有嵌套层级）。
    """
    def run(self):
        self.log("DemoNestFlow: 入口，调用第1层...")
        result = self.run_flow(self.DemoNestLevel1Flow)
        self.log(f"DemoNestFlow: 收到第1层返回: {result}")
        return {"level": 0, "message": "嵌套演示完成"}

    class DemoNestLevel1Flow(BaseWorkflow):
        def run(self):
            self.log("进入第1层，准备调用第2层...")
            result = self.run_flow(DemoNestFlow.DemoNestLevel2Flow)
            self.log(f"第1层收到第2层返回: {result}")
            return {"level": 1, "message": "第1层执行完成"}

    class DemoNestLevel2Flow(BaseWorkflow):
        def run(self):
            self.log("进入第2层，准备调用第3层...")
            result = self.run_flow(DemoNestFlow.DemoNestLevel3Flow)
            self.log(f"第2层收到第3层返回: {result}")
            return {"level": 2, "message": "第2层执行完成"}

    class DemoNestLevel3Flow(BaseWorkflow):
        def run(self):
            self.log("进入第3层，准备调用第4层...")
            result = self.run_flow(DemoNestFlow.DemoNestLevel4Flow)
            self.log(f"第3层收到第4层返回: {result}")
            return {"level": 3, "message": "第3层执行完成"}

    class DemoNestLevel4Flow(BaseWorkflow):
        def run(self):
            self.log("这是第4层，最底层。")
            return {"level": 4, "message": "第4层执行完成"} 