# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
from core.constants import WorkflowStatus
import subprocess
import threading
import platform

class BatFlow(BaseWorkflow):
    """
    执行一条bat/shell命令。
    支持wait参数，wait=True时等待命令执行完。
    支持close参数，close=True时窗口自动关闭。
    支持finished_func参数，命令完成后执行回调函数。
    支持enable_logging参数，控制是否写入日志。
    """
    DEFAULT_PARAMS = {
        "wait": True,
        "close": True,
        "finished_func": None,
        "enable_bat_log": True,
    }

    def init(self):
        self.wait = self.get_param('wait', True)
        self.close = self.get_param('close', True)
        self.finished_func = self.get_param('finished_func', None)
        self.enable_bat_log = self.get_param('enable_bat_log', True)

    def run(self):
        return self.execute_cmd()
    
    def execute_cmd(self):
        """执行命令，支持同步和异步模式"""
        cmd = self.get_param('cmd')
        if not cmd:
            self.log("错误：'BatFlow' 工作流需要一个 'cmd' 参数。")
            return {"status": WorkflowStatus.ERROR.value, "message": "缺少cmd参数"}
        return self._execute_command(cmd)
    
    def _execute_command(self, cmd):
        """执行命令的核心方法，可以被子类继承"""
        
        self.log(f"$ {cmd}")
        
        if self.wait:
            # 同步执行
            result = self._run_and_log(cmd)
            if self.close:
                self._call_finished_callback()
            return result
        else:
            # 异步执行
            threading.Thread(
                target=self._async_run, 
                args=(cmd, self.close), 
                daemon=True
            ).start()
            return {"status": WorkflowStatus.ASYNC.value, "message": "命令正在异步执行"}

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
            if self.enable_bat_log:
                for line in process.stdout:
                    if line.strip():
                        self.log(line.strip())
            
            process.wait()
            
            # 返回执行结果
            if process.returncode == 0:
                return {"status": WorkflowStatus.SUCCESS.value, "message": "命令执行成功", "returncode": process.returncode}
            else:
                return {"status": WorkflowStatus.ERROR.value, "message": f"命令执行失败，返回码: {process.returncode}", "returncode": process.returncode}
                
        except Exception as e:
            self.log(f"命令执行出错: {e}")
            return {"status": WorkflowStatus.ERROR.value, "message": f"命令执行异常: {str(e)}"}

    def _call_finished_callback(self):
        """调用完成回调函数"""
        if self.finished_func:
            self.finished_func()