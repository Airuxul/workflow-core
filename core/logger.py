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
        logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", level="INFO", backtrace=False, diagnose=False)
        logger.add("logs/workflow.log", rotation="10 MB", encoding="utf-8", level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}")
        logger.add("logs/workflow.log", rotation="10 MB", encoding="utf-8", level="ERROR", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {file}:{line} | {message}")
        WorkflowLogger._inited = True

    def info(self, msg):
        from loguru import logger
        logger.info(msg)

    def warning(self, msg):
        from loguru import logger
        logger.warning(msg)

    def error(self, msg):
        from loguru import logger
        logger.error(msg)

    def exception(self, msg):
        from loguru import logger
        logger.exception(msg) 