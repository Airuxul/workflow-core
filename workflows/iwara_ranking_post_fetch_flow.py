# -*- coding: utf-8 -*-

import os
import re
import json
import requests
from core import constants
from core.workflow import BaseWorkflow
from core.utils import safe_filename
from .iwara_download_flow import IwaraDownloadFlow


class IwaraRankingPostFetchFlow(BaseWorkflow):
    """
    自动获取Iwara Rank专用作者的最新排行榜文章，提取视频信息并批量下载。
    """
    DEFAULT_PARAMS = {
        "username": "",       # Iwara邮箱
        "password": "",       # Iwara密码
        "save_path": "downloads",
        "resolution": "Source"
    }

    def run(self):
        self.log("CLI PARAMS:", self.config.params)
        save_path = self.get_param("save_path")
        resolution = self.get_param("resolution")

        # 直接用写死的rank作者ID
        posts_url = f"{constants.IWARA_API_BASE}/posts?page=0&user={constants.IWARA_RANK_USER_ID}"
        self.log(f"正在获取用户文章列表: {posts_url}")
        try:
            resp = requests.get(posts_url)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            self.log(f"获取用户文章列表失败: {e}")
            return
        results = data.get('results', [])
        if not results:
            self.log("未获取到任何文章。")
            return
        post = results[0]
        post_id = post.get('id')
        post_title = post.get('title', f"Iwara排行榜_{post_id}")
        self.log(f"最新文章: {post_title} (id={post_id})")
        # 获取文章详情
        api_url = f"{constants.IWARA_API_BASE}/post/{post_id}"
        self.log(f"正在通过API获取排行榜信息: {api_url}")
        try:
            resp = requests.get(api_url)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            self.log(f"获取排行榜API失败: {e}")
            return
        body = data.get("body", "")
        # 解析视频信息
        video_blocks = re.split(r'### ', body)[1:]
        video_list = []
        for block in video_blocks:
            m = re.match(r'#?(\d+)[^\n]*?([\u4e00-\u9fa5A-Za-z0-9\[\]& ]+)?', block)
            index = m.group(1) if m else None
            title = m.group(2).strip() if m and m.group(2) else None
            view_like = re.search(r'【View】([\d\.k]+)[^\d]+【Like】([\d\.k]+)', block)
            views = view_like.group(1) if view_like else None
            likes = view_like.group(2) if view_like else None
            img = re.search(r'!\[\]\((https://[\w\./-]+)\)', block)
            img_url = img.group(1) if img else None
            vid = re.search(r'https://www\\.iwara\\.tv/video/([a-zA-Z0-9]+)', block)
            if not vid:
                vid = re.search(r'https://www\.iwara\.tv/video/([a-zA-Z0-9]+)', block)
            video_id = vid.group(1) if vid else None
            if video_id:
                video_list.append({
                    "index": index,
                    "title": title,
                    "views": views,
                    "likes": likes,
                    "img_url": img_url,
                    "video_id": video_id
                })
        # 排序
        def parse_num(s):
            if not s:
                return 0
            s = s.lower().replace('k', '000')
            try:
                return int(float(s))
            except:
                return 0
        view_sorted = sorted(video_list, key=lambda x: parse_num(x['views']), reverse=True)
        likes_sorted = sorted(video_list, key=lambda x: parse_num(x['likes']), reverse=True)
        # 支持html和txt模板两种方式
        html_template_path = os.path.join(os.path.dirname(__file__), f'../{constants.TEMPLATE_DIR}/iwara_ranking_template.txt')
        template = None
        html = None
        if os.path.exists(html_template_path):
            with open(html_template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            html = template % (
                post_title,
                post_title,
                json.dumps(view_sorted, ensure_ascii=False),
                json.dumps(likes_sorted, ensure_ascii=False)
            )
        # 输出HTML
        output_html = f"{constants.TEMP_DIR}/{safe_filename(post_title)}.html"
        out_dir = os.path.dirname(output_html)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html or '')
        print("输出HTML：", output_html)
        # 可选：自动批量下载
        if video_list and False:
            self.log("开始批量下载视频...")
            video_ids = ','.join([v['video_id'] for v in video_list])
            self.run_flow(IwaraDownloadFlow, params={
                "video_ids": video_ids,
                "save_path": save_path,
                "resolution": resolution
            })
            self.log("全部流程结束。")