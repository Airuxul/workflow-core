# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
import subprocess
import threading
import platform

class BatFlow(BaseWorkflow):
    """
    执行一条bat/shell命令。
    支持wait参数，wait=True时等待命令执行完。
    支持close参数，close=True时窗口自动关闭。
    支持finished_func参数，命令完成后执行回调函数。
    """
    DEFAULT_PARAMS = {
        "wait": True,
        "close": True,
        "finished_func": None,
    }

    def run(self):
        """执行命令，支持同步和异步模式"""
        cmd = self.get_param('cmd')
        if not cmd:
            self.log("错误：'BatFlow' 工作流需要一个 'cmd' 参数。")
            return
        
        wait = self.get_param('wait', True)
        close = self.get_param('close', True)
        
        self.log(f"$ {cmd}")
        
        if wait:
            # 同步执行
            self._run_and_log(cmd)
            if close:
                self._call_finished_callback()
        else:
            # 异步执行
            threading.Thread(
                target=self._async_run, 
                args=(cmd, close), 
                daemon=True
            ).start()

    def _async_run(self, cmd, close):
        """异步执行命令"""
        self._run_and_log(cmd)
        if close:
            self._call_finished_callback()

    def _run_and_log(self, cmd):
        """执行命令并实时将输出转发到日志"""
        try:
            # 根据操作系统选择合适的编码
            encoding = 'gbk' if platform.system() == "Windows" else 'utf-8'
            
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                encoding=encoding, 
                errors='replace'
            )
            
            # 实时输出日志
            for line in process.stdout:
                if line.strip():
                    self.log(line.strip())
            
            process.wait()
            
        except Exception as e:
            self.log(f"命令执行出错: {e}")

    def _call_finished_callback(self):
        """调用完成回调函数"""
        finished_func = self.get_param('finished_func')
        if finished_func:
            finished_func()