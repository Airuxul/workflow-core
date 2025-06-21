# -*- coding: utf-8 -*-

from core.workflow import BaseWorkflow
from pathlib import Path
from datetime import datetime, timedelta

class VideoCopyFlow(BaseWorkflow):
    """
    视频复制工作流。
    """
    DEFAULT_PARAMS = {
        "source_dir": "D:\\video",
        "target_dir": "D:\\video_copy",
        "file_type": [
            ".mp4", 
            ".avi",
        ],
        "max_age_hours": 24, # 默认24小时内
    }

    def run(self):
        """
        执行视频复制，并返回一个包含(源路径, 目标路径)的元组列表。
        """
        source_dir_str = self.get_param("source_dir")
        target_dir_str = self.get_param("target_dir")
        file_types = self.get_param("file_type")
        max_age_hours_str = self.get_param("max_age_hours")
        max_age_hours = int(max_age_hours_str) if max_age_hours_str is not None else None

        source_path = Path(source_dir_str)
        target_path = Path(target_dir_str)

        if not source_path.is_dir():
            self.log(f"错误: 源目录 '{source_path}' 不存在或不是一个目录。")
            return []

        self.log(f"开始扫描源目录: {source_path}")
        self.log(f"文件将复制到: {target_path}")
        self.log(f"允许的文件类型: {file_types}")
        if max_age_hours is not None:
            self.log(f"文件修改时间限制: 最近 {max_age_hours} 小时内")

        target_path.mkdir(parents=True, exist_ok=True)

        copied_files_info = []
        now = datetime.now()

        for file in source_path.rglob('*'):
            if file.is_file() and file.suffix.lower() in file_types:
                
                if max_age_hours is not None:
                    file_mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                    if now - file_mod_time > timedelta(hours=max_age_hours):
                        continue

                dest_file = target_path / file.name
                
                if dest_file.exists():
                    self.log(f"- 跳过 (文件已存在): {dest_file}")
                    copied_files_info.append((file, dest_file))
                    continue

                self.log(f"- 正在复制: {file.name} -> {dest_file}")
                try:
                    import shutil
                    shutil.copy2(file, dest_file)
                    copied_files_info.append((file, dest_file))
                except Exception as e:
                    self.log(f"  复制文件时出错: {e}")

        self.log(f"复制完成！总共处理了 {len(copied_files_info)} 个视频文件。")
        return copied_files_info