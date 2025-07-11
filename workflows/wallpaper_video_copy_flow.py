# -*- coding: utf-8 -*-

import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from core.workflow import BaseWorkflow
from core.utils import safe_filename

class WallpaperVideoCopyFlow(BaseWorkflow):
    """
    壁纸视频复制工作流：先读取project.json获取重命名信息，然后复制并重命名视频文件。
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
    
    def get_rename_info(self, source_dir):
        """
        扫描源目录，获取所有project.json文件的重命名信息。
        返回: {视频文件路径: 重命名后的文件名}
        """
        rename_info = {}
        source_path = Path(source_dir)
        
        if not source_path.is_dir():
            self.log(f"错误: 源目录 '{source_path}' 不存在或不是一个目录。")
            return rename_info
            
        self.log(f"扫描源目录获取重命名信息: {source_path}")
        
        for project_json in source_path.rglob('project.json'):
            try:
                with open(project_json, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                title = project_data.get('title')
                if not title:
                    continue
                    
                sanitized_title = safe_filename(title)
                
                # 查找同目录下的视频文件
                video_dir = project_json.parent
                for video_file in video_dir.glob('*'):
                    if video_file.is_file() and video_file.suffix.lower() in self.get_param("file_type"):
                        new_filename = sanitized_title + video_file.suffix
                        rename_info[video_file] = new_filename
                        self.log(f"- 找到重命名映射: {video_file.name} -> {new_filename}")
                        
            except json.JSONDecodeError:
                self.log(f"- 错误: 解析 {project_json} 失败，跳过。")
            except Exception as e:
                self.log(f"- 处理 {project_json} 时发生错误: {e}")
                
        return rename_info
    
    def run(self):
        """
        执行壁纸视频复制工作流。
        """
        today_str = datetime.now().strftime('%Y_%m_%d')
        self.set_shared_value("cur_date_day", today_str)
        self.log(f"动态设置当天日期为: {today_str}")

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

        # 获取重命名信息
        rename_info = self.get_rename_info(source_dir_str)
        if not rename_info:
            self.log("未找到任何有效的project.json文件或视频文件。")
            return []

        # 执行复制
        now = datetime.now()
        copied_files_info = []
        failed_files_info = []
        
        for video_file, new_filename in rename_info.items():
            # 检查文件年龄限制
            if max_age_hours is not None:
                file_mod_time = datetime.fromtimestamp(video_file.stat().st_mtime)
                if now - file_mod_time > timedelta(hours=max_age_hours):
                    self.log(f"- 跳过 (文件过旧): {video_file.name}")
                    continue

            dest_file = target_path / new_filename
            
            if dest_file.exists():
                self.log(f"- 跳过 (文件已存在): {dest_file}")
                continue

            try:
                shutil.copy2(video_file, dest_file)
                self.log(f"- 正在复制: {video_file.name} -> {dest_file}")
                copied_files_info.append((video_file, dest_file))
            except Exception as e:
                self.log(f"  复制文件时出错: {e}")
                failed_files_info.append((video_file, dest_file, str(e)))

        self.log(f"复制完成！成功复制 {len(copied_files_info)} 个视频文件。")
        if failed_files_info:
            self.log(f"复制失败 {len(failed_files_info)} 个文件：")
            for file, dest_file, err in failed_files_info:
                self.log(f"  {file} -> {dest_file}, 错误: {err}")
        
        return copied_files_info 