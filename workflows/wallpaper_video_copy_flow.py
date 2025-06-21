# -*- coding: utf-8 -*-

import json
import re
from pathlib import Path
from datetime import datetime

from core.workflow import BaseWorkflow
from .video_copy_flow import VideoCopyFlow

class WallpaperVideoCopyFlow(BaseWorkflow):
    """
    一个组合工作流，先复制视频，然后根据壁纸引擎的project.json文件重命名它们。
    """
    DEFAULT_PARAMS = {
        "source_dir": "E:\\Steam\\steamapps\\workshop\\content\\431960",
        "target_dir": "E:\\{{cur_date_day}}",
        "file_type": [
            ".mp4",
            ".avi",
            ".mkv",
        ],
        "max_age_hours": 24,
    }
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """
        替换Windows文件名中的非法字符为空格。
        """
        return re.sub(r'[\\/*?:"<>|]', ' ', name)

    def run(self):
        """
        执行组合工作流。
        """
        today_str = datetime.now().strftime('%Y_%m_%d')
        self.set_shared_value("cur_date_day", today_str)
        self.log(f"动态设置当天日期为: {today_str}")

        copied_files_info = self.run_flow(VideoCopyFlow)
        
        if not copied_files_info:
            self.log("视频复制流程没有返回任何文件，或执行失败。流程中止。")
            return

        self.log(f"根据 project.json 重命名 {len(copied_files_info)} 个文件...")
        renamed_count = 0
        for source_file, dest_file in copied_files_info:
            source_file = Path(source_file)
            dest_file = Path(dest_file)
            project_json_path = source_file.parent / 'project.json'

            if not project_json_path.exists():
                self.log(f"- 跳过: 在 {source_file.parent} 中未找到 project.json。")
                continue
            
            try:
                with open(project_json_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                title = project_data.get('title')
                if not title:
                    self.log(f"- 跳过: {project_json_path} 中没有 'title' 字段。")
                    continue
                
                sanitized_title = self._sanitize_filename(title)
                new_filename = sanitized_title + dest_file.suffix
                new_dest_path = dest_file.parent / new_filename

                if dest_file.exists():
                    if dest_file == new_dest_path:
                        self.log(f"- 无需重命名: {dest_file.name}")
                        continue
                        
                    self.log(f"- 正在重命名: {dest_file.name} -> {new_dest_path.name}")
                    dest_file.rename(new_dest_path)
                    renamed_count += 1
                else:
                    self.log(f"- 警告: 目标文件 {dest_file} 不存在，无法重命名。")

            except json.JSONDecodeError:
                self.log(f"- 错误: 解析 {project_json_path} 失败，跳过。")
            except Exception as e:
                self.log(f"- 处理文件 {source_file.name} 时发生未知错误: {e}")

        self.log(f"重命名完成！总共重命名了 {renamed_count} 个文件。") 