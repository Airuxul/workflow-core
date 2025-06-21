# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
import sys

class SysVersionCheckFlow(BaseWorkflow):
    """
    检查并打印当前的Python版本。
    """
    def run(self):
        """
        执行版本检查。
        """
        self.log(f"Python版本: {sys.version}") 