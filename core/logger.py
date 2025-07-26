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
        
        # 控制台日志配置
        console_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        logger.add(sys.stdout, format=console_format, level="INFO", backtrace=False, diagnose=False)
        
        # 文件日志配置
        file_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
        error_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {file}:{line} | {message}"
        
        logger.add("logs/workflow.log", rotation="10 MB", encoding="utf-8", level="INFO", format=file_format)
        logger.add("logs/workflow.log", rotation="10 MB", encoding="utf-8", level="ERROR", format=error_format)
        
        WorkflowLogger._inited = True

    def _log(self, level, msg):
        """统一的日志记录方法"""
        from loguru import logger
        getattr(logger, level)(msg)

    def info(self, msg):
        self._log('info', msg)

    def warning(self, msg):
        self._log('warning', msg)

    def error(self, msg):
        self._log('error', msg)

    def exception(self, msg):
        self._log('exception', msg) 