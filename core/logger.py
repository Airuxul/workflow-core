# -*- coding: utf-8 -*-

class WorkflowLogger:
    """
    单例日志工具类，封装loguru，支持全局调用。
    """
    _instance = None
    _inited = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = WorkflowLogger()
        if not cls._inited:
            cls._instance._init_logger()
        return cls._instance

    def _init_logger(self):
        from loguru import logger
        import sys
        import os
        
        os.makedirs('logs', exist_ok=True)
        logger.remove()
        
        # 统一的日志格式配置
        formats = {
            'console': "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            'file': "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            'error': "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {file}:{line} | {message}"
        }
        
        # 控制台日志配置
        logger.add(sys.stdout, format=formats['console'], level="INFO", backtrace=False, diagnose=False)
        
        # 文件日志配置
        logger.add("logs/workflow.log", rotation="10 MB", encoding="utf-8", level="INFO", format=formats['file'])
        logger.add("logs/workflow.log", rotation="10 MB", encoding="utf-8", level="ERROR", format=formats['error'])
        
        WorkflowLogger._inited = True

    def _log(self, level, msg):
        """统一的日志记录方法"""
        from loguru import logger
        getattr(logger, level)(msg)

    def __getattr__(self, name):
        """动态处理日志方法调用"""
        if name in ['info', 'warning', 'error', 'exception', 'debug', 'critical']:
            def log_method(msg):
                self._log(name, msg)
            return log_method
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'") 