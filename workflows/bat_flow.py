# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
import os

class BatFlow(BaseWorkflow):
    """
    执行一条bat/shell命令。
    """
    def run(self):
        """
        从配置中读取'cmd'参数并执行。
        """
        cmd = self.get_param('cmd')
        if cmd:
            self.log(f"$ {cmd}")
            os.system(cmd)
        else:
            self.log("错误：'BatFlow' 工作流需要一个 'cmd' 参数。") 