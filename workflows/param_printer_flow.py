# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow

class ParamPrinterFlow(BaseWorkflow):
    """
    一个简单的流程，用于打印出它接收到的'msg'参数。
    """
    def run(self):
        """
        从配置中获取'msg'参数并打印。
        """
        message = self.get_param('msg', '没有提供消息。')
        self.log(f"[打印机]: {message}")