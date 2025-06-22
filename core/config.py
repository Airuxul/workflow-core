# -*- coding: utf-8 -*-

from __future__ import annotations
import re

class Config:
    """
    一个分层的配置类，支持作用域链和"即时"参数解析。
    """
    def __init__(self, params: dict | None = None, parent: Config | None = None):
        """
        :param params: 当前层级的参数。
        :param parent: 父级Config实例。
        """
        self._parent = parent
        self._params = params if params is not None else {}

    def _get_raw_param(self, key: str, default=None):
        """优先查找父级参数，再查本地参数。"""
        if self._parent:
            value = self._parent._get_raw_param(key, None)
            if value is not None:
                return value
        if key in self._params:
            return self._params[key]
        return default

    def _resolve_placeholders(self, value_to_resolve):
        """递归解析字符串中的占位符。"""
        if not isinstance(value_to_resolve, str):
            return value_to_resolve
        
        placeholders = re.findall(r"\{\{([\w_]+)\}\}", value_to_resolve)
        if not placeholders:
            return value_to_resolve
            
        for placeholder in placeholders:
            # 使用 get_param 来获取占位符的值，这会触发进一步的递归解析
            resolved_value = self.get_param(placeholder, '')
            value_to_resolve = value_to_resolve.replace(f"{{{{{placeholder}}}}}", str(resolved_value))
            
        return value_to_resolve

    @property
    def params(self) -> dict:
        """递归获取合并后的所有有效参数，并解析它们。"""
        parent_params = self._parent.params if self._parent else {}
        # 先合并，再对合并后的结果进行解析
        merged_params = {**parent_params, **self._params}
        for key, value in merged_params.items():
            merged_params[key] = self._resolve_placeholders(value)
        return merged_params

    def get_param(self, key: str, default=None):
        """
        按优先级获取单个参数的原始值，并"即时"解析它。
        """
        raw_value = self._get_raw_param(key, default)
        return self._resolve_placeholders(raw_value) 