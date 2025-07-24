# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
import subprocess
import threading
from core.logger import WorkflowLogger

class BatFlow(BaseWorkflow):
    """
    执行一条bat/shell命令。
    支持wait参数，wait=True时等待命令执行完。
    支持close参数，close=True时窗口自动关闭。
    支持finished_event参数，finished_event=True时触发事件。
    """
    DEFAULT_PARAMS = {
        "wait": True,
        "close": True,
        "finished_func": None,
    }

    def run(self):
        """
        从配置中读取'cmd'参数并执行。
        支持wait参数，wait=True时等待命令执行完。
        支持close参数，close=True时窗口自动关闭。
        支持异步+回调：wait=False时用线程异步执行，命令结束后自动回调。
        输出实时转发到日志。
        """
        cmd = self.get_param('cmd')
        wait = self.get_param('wait', False)
        close = self.get_param('close', True)
        if cmd:
            self.log(f"$ {cmd}")
            if wait:
                self._run_and_log(cmd)
                if close:
                    self.on_cmd_finished()
            else:
                def run_and_callback():
                    self._run_and_log(cmd)
                    if close:
                        self.on_cmd_finished()
                threading.Thread(target=run_and_callback, daemon=True).start()
        else:
            self.log("错误：'BatFlow' 工作流需要一个 'cmd' 参数。")

    def _run_and_log(self, cmd):
        """
        执行命令并实时将输出转发到日志。
        """
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in p.stdout:
            self.log(line.rstrip())
        p.wait()

    def on_cmd_finished(self):
        """
        命令执行完成后的回调，wait=True且close=True时触发。
        """
        finished_func = self.get_param('finished_func')
        if finished_func:
            finished_func()