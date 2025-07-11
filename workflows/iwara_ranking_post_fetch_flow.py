# -*- coding: utf-8 -*-

import os
import re
import json
import requests
from dataclasses import dataclass, asdict
from typing import Optional
from core import constants
from core.workflow import BaseWorkflow
from .iwara_video_download_flow import IwaraVideoDownloadFlow


@dataclass
class IwaraVideo:
    """Iwara视频信息类"""
    rank: str                    # 排名 (P1, P2, P3 或 1, 2, 3, 52, 54等)
    title: str                   # 视频标题
    category: str                # 视频分类 (SEX, DANCE, SEX&DANCE)
    views: str                   # 播放量
    likes: str                   # 点赞数
    video_id: str                # 视频ID
    img_url: Optional[str] = None  # 封面图片URL
    percentage: Optional[str] = None  # 百分比 (仅PICKUP视频有)
    
    def to_dict(self):
        """转换为字典格式"""
        return asdict(self)
    
    def is_pickup(self) -> bool:
        """判断是否为PICKUP视频"""
        return self.rank.startswith('P')
    
    def get_rank_number(self) -> int:
        """获取排名数字"""
        if self.is_pickup():
            return int(self.rank[1:])
        return int(self.rank)
    
    def get_sort_key(self) -> tuple:
        """获取排序键"""
        if self.is_pickup():
            return (0, self.get_rank_number())  # PICKUP排在前面
        return (1, self.get_rank_number())      # 正常排名按数字排序


class IwaraRankingPostFetchFlow(BaseWorkflow):
    """
    自动获取Iwara Rank专用作者的最新排行榜文章，提取视频信息并批量下载。
    """
    DEFAULT_PARAMS = {
        "username": "", # 必填，Iwara邮箱
        "password": "", # 必填，Iwara密码
        "save_path": "downloads", # 可选，下载保存路径
        "resolution": "Source", # 可选，下载清晰度
        "max_rank": 10, # 可选，只下载排名小于等于此值的视频（PICKUP视频不受此限制）
        "enable_download": False # 可选，是否启用自动下载功能
    }

    def get_latest_post(self):
        """获取最新的排行榜文章"""
        posts_url = f"{constants.IWARA_API_BASE}/posts?page=0&user={constants.IWARA_RANK_USER_ID}"
        self.log(f"正在获取用户文章列表: {posts_url}")
        try:
            resp = requests.get(posts_url)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            self.log(f"获取用户文章列表失败: {e}")
            return None
        
        results = data.get('results', [])
        if not results:
            self.log("未获取到任何文章。")
            return None
        
        post = results[0]
        post_id = post.get('id')
        post_title = post.get('title', f"Iwara排行榜_{post_id}")
        self.log(f"最新文章: {post_title} (id={post_id})")
        
        return {
            'id': post_id,
            'title': post_title
        }

    def fetch_post_content(self, post_id):
        """获取文章详细内容"""
        api_url = f"{constants.IWARA_API_BASE}/post/{post_id}"
        self.log(f"正在通过API获取排行榜信息: {api_url}")
        try:
            resp = requests.get(api_url)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            self.log(f"获取排行榜API失败: {e}")
            return None
        
        return data.get("body", "")

    def parse_pickup_videos(self, body) -> list[IwaraVideo]:
        """解析PICKUP部分的视频"""
        video_list = []
        pickup_pattern = r'### (P\d+)(?:\(([\d\.]+)%\))?\s*([^\n]+)?\n\n\[([^\]]+)\]【View】([\d\.k]+)【Like】(\d+)\n\n(?:!\[\]\((https://[^\s]+)\)\s*\n)?(https://www\.iwara\.tv/video/([a-zA-Z0-9]+))'
        pickup_matches = re.finditer(pickup_pattern, body)
        
        for match in pickup_matches:
            pickup_rank = match.group(1)  # P1, P2, P3
            percentage = match.group(2)   # 百分比
            title = match.group(3)        # 标题
            category = match.group(4)     # 分类
            views = match.group(5)        # 播放量
            likes = match.group(6)        # 点赞数
            img_url = match.group(7)      # 封面图片
            video_id = match.group(9)     # 视频ID
            
            video = IwaraVideo(
                rank=pickup_rank,
                title=title.strip() if title else "",
                category=category,
                views=views,
                likes=likes,
                video_id=video_id,
                img_url=img_url,
                percentage=percentage
            )
            video_list.append(video)
        
        return video_list

    def parse_ranked_videos(self, body) -> list[IwaraVideo]:
        """解析排行榜部分的视频"""
        video_list = []
        # 合并的正则表达式：匹配所有排名格式
        # 匹配 #1(1st), #2(2nd), #3(3rd), (5th), (6th), #17(52th), #18(54th) 等格式
        rank_pattern = r'(?:## (#\d+)\(|### \()(\d+)(?:st|nd|rd|th)\)\s*([^\n]+)?\n\n\[([^\]]+)\]【View】([\d\.k]+)\((\d+)(?:st|nd|rd|th)\)【Like】(\d+)\((\d+)(?:st|nd|rd|th)\)\n\n(?:!\[\]\((https://[^\s]+)\)\s*\n)?(https://www\.iwara\.tv/video/([a-zA-Z0-9]+))'
        rank_matches = re.finditer(rank_pattern, body)
        
        for match in rank_matches:
            rank_num = match.group(2)     # 1, 2, 3, 5, 6, 52, 54
            title = match.group(3)        # 标题
            category = match.group(4)     # 分类
            views = match.group(5)        # 播放量
            likes = match.group(7)        # 点赞数
            img_url = match.group(9)      # 封面图片
            video_id = match.group(11)    # 视频ID
            
            video = IwaraVideo(
                rank=rank_num,
                title=title.strip() if title else "",
                category=category,
                views=views,
                likes=likes,
                video_id=video_id,
                img_url=img_url
            )
            video_list.append(video)
        
        return video_list

    def sort_videos(self, video_list: list[IwaraVideo]) -> list[IwaraVideo]:
        """按rank排序视频列表"""
        return sorted(video_list, key=lambda video: video.get_sort_key())

    def build_json_data(self, post_info, video_list: list[IwaraVideo]):
        """构建JSON数据结构"""
        return {
            "post_title": post_info['title'],
            "post_id": post_info['id'],
            "fetch_time": requests.get("https://worldtimeapi.org/api/timezone/Asia/Shanghai").json().get("datetime", ""),
            "total_videos": len(video_list),
            "videos": [video.to_dict() for video in video_list]
        }

    def save_json_file(self, json_data):
        """保存JSON文件"""
        output_json = f"{constants.TEMP_DIR}/iwara_videos.json"
        out_dir = os.path.dirname(output_json)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        self.log("输出JSON：", output_json)
        return output_json

    def run(self):
        """主执行方法"""
        self.log("CLI PARAMS:", self.config.params)
        
        # 获取最新文章信息
        post_info = self.get_latest_post()
        if not post_info:
            return
        
        # 获取文章内容
        body = self.fetch_post_content(post_info['id'])
        if not body:
            return
        
        # 解析视频信息
        pickup_videos = self.parse_pickup_videos(body)
        ranked_videos = self.parse_ranked_videos(body)
        
        # 合并所有视频
        all_videos = pickup_videos + ranked_videos
        
        # 排序
        sorted_videos = self.sort_videos(all_videos)
        
        # 构建JSON数据
        json_data = self.build_json_data(post_info, sorted_videos)
        
        # 保存文件
        self.save_json_file(json_data)
        
        # 可选：自动批量下载
        enable_download = self.get_param("enable_download", False)
        if all_videos and enable_download:
            self.log("开始批量下载视频...")
            
            # 根据max_rank参数过滤视频
            max_rank = self.get_param("max_rank", 10)
            filtered_videos = []
            
            for video in all_videos:
                if video.is_pickup():
                    # PICKUP视频不受排名限制
                    filtered_videos.append(video)
                    self.log(f"包含PICKUP视频: {video.rank} - {video.title}")
                elif video.get_rank_number() <= int(max_rank):
                    # 普通视频只有排名小于等于max_rank才下载
                    filtered_videos.append(video)
                    self.log(f"包含排名视频: #{video.rank} - {video.title}")
                else:
                    self.log(f"跳过排名视频: #{video.rank} - {video.title} (超过max_rank={max_rank})")
            
            if filtered_videos:
                video_ids = ','.join([v.video_id for v in filtered_videos])
                self.log(f"准备下载 {len(filtered_videos)} 个视频 (max_rank={max_rank})")
                self.run_flow(IwaraVideoDownloadFlow, params={
                    "video_ids": video_ids,
                    "save_path": self.get_param("save_path"),
                    "resolution": self.get_param("resolution")
                })
            else:
                self.log(f"没有符合条件的视频需要下载 (max_rank={max_rank})")
            
            self.log("全部流程结束。")
        elif all_videos and not enable_download:
            self.log("跳过自动下载 (enable_download=False)")
        else:
            self.log("没有视频数据，跳过下载")