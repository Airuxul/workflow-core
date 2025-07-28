# -*- coding: utf-8 -*-

"""
通用工具类，提供常用的工具方法
"""

from typing import Any, Dict, List

class Utils:
    """通用工具类"""
    
    @staticmethod
    def merge_dicts(*dicts: Dict) -> Dict:
        """
        合并多个字典，后面的字典会覆盖前面的
        
        :param dicts: 要合并的字典
        :return: 合并后的字典
        """
        result = {}
        for d in dicts:
            if d:
                result.update(d)
        return result
    
    @staticmethod
    def exclude_dict(dictionary: Dict, keys: List[str]) -> Dict:
        """
        从字典中排除指定的键
        
        :param dictionary: 源字典
        :param keys: 要排除的键列表
        :return: 过滤后的字典
        """
        return {k: v for k, v in dictionary.items() if k not in keys}
    
    @staticmethod
    def format_message(template: str, **kwargs) -> str:
        """
        格式化消息模板
        
        :param template: 消息模板
        :param kwargs: 要替换的参数
        :return: 格式化后的消息
        """
        return template.format(**kwargs)
    
    @staticmethod
    def is_valid_workflow_class(obj: Any) -> bool:
        """
        检查对象是否为有效的工作流类
        
        :param obj: 要检查的对象
        :return: 是否为有效的工作流类
        """
        from core.workflow import BaseWorkflow
        return (hasattr(obj, '__class__') and 
                issubclass(obj, BaseWorkflow) and 
                obj is not BaseWorkflow)
    
    @staticmethod
    def flow_name_to_class_name(flow_name: str) -> str:
        """
        将 flow_name（如 main_test_flow）转换为类名（如 MainTestFlow）。
        如果已经以 Flow 结尾，不再重复加。
        """
        class_name = ''.join(word.capitalize() for word in flow_name.replace('-', '_').split('_'))
        return class_name
    
    @staticmethod
    def parse_key_value_pairs(args_list: List[str], key_prefix: str = '--') -> dict:
        """
        通用的键值对解析方法
        
        :param args_list: 参数列表
        :param key_prefix: 键的前缀，默认为'--'
        :return: 解析后的参数字典
        """
        params = {}
        for i in range(0, len(args_list), 2):
            if i + 1 >= len(args_list):
                break
                
            key_with_prefix = args_list[i]
            value = args_list[i + 1]
            
            if key_with_prefix.startswith(key_prefix):
                key = key_with_prefix[len(key_prefix):]
                params[key] = value
        
        return params
    
    @staticmethod
    def parse_cmd_args():
        """
        解析命令行所有 --key value 参数为 dict。
        """
        import argparse
        parser = argparse.ArgumentParser(description="工作流执行引擎")
        _, unknown = parser.parse_known_args()
        return Utils.parse_key_value_pairs(unknown, '-') 