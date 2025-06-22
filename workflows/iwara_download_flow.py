# -*- coding: utf-8 -*-

import os
import requests
import hashlib
from requests.auth import AuthBase
from core.workflow import BaseWorkflow
from core import constants

class BearerAuth(AuthBase):
    """Bearer Authentication for Iwara API"""
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.token
        return r

class IwaraDownloadFlow(BaseWorkflow):
    """
    通过邮箱和密码登录 Iwara API，批量下载指定 video_ids 的视频。
    """
    DEFAULT_PARAMS = {
        "username": "",       # Iwara邮箱
        "password": "",       # Iwara密码
        "video_ids": "",      # 视频ID，多个ID用逗号分隔 (例如: "video1,video2")
        "save_path": "downloads", # 视频保存的目录
        "resolution": "Source" # 下载分辨率 (例如: Source, 1080p, 720p, 540p, 360p)
    }

    def __init__(self, manager, config):
        super().__init__(manager, config)
        self.api_url = constants.IWARA_API_BASE
        self.file_url = constants.IWARA_FILE_BASE
        self.token = None
        self.timeout = 30
        self.download_timeout = 300

    def login(self, email, password):
        if not email or not password:
            self.log('未提供邮箱和密码，跳过登录')
            return True
        url = self.api_url + '/user/login'
        json_data = {'email': email, 'password': password}
        r = requests.post(url, json=json_data, timeout=self.timeout)
        try:
            self.token = r.json()['token']
            self.log('API Login success')
            return True
        except Exception as e:
            self.log(f'API Login failed: {e}')
            return False

    def get_video(self, video_id):
        url = self.api_url + '/video/' + video_id
        r = requests.get(url, auth=BearerAuth(self.token), timeout=self.timeout)
        if r.status_code != 200:
            self.log(f"获取视频信息失败: {video_id}")
            return None
        return r.json()

    def download_video(self, video_id, info, save_path, resolution):
        # 兼容 fileUrl 直链和资源列表
        if 'fileUrl' in info:
            url = info['fileUrl']
            file_id = info['file']['id']
            expires = url.split('/')[4].split('?')[1].split('&')[0].split('=')[1]
            SHA_postfix = "_5nFp9kmbNnHdAFhaqMvt"
            SHA_key = file_id + "_" + expires + SHA_postfix
            hash_val = hashlib.sha1(SHA_key.encode('utf-8')).hexdigest()
            headers = {"X-Version": hash_val}
            resources = requests.get(url, headers=headers, auth=BearerAuth(self.token), timeout=self.timeout).json()
            # 选择分辨率
            resource = None
            for res in resources:
                if res['name'] == resolution:
                    resource = res
                    break
            if not resource:
                self.log(f"未找到分辨率为{resolution}的下载链接: {video_id}")
                return
            download_link = "https:" + resource['src']['download']
            file_type = resource['type'].split('/')[1]
            video_file_name = info.get('title', video_id) + '.' + file_type
            else:
            # 兼容旧API
            files = info.get('files', [])
            download_link = None
            for file in files:
                if file.get('resolution') == resolution:
                    download_link = file.get('uri')
                    break
            if not download_link:
                self.log(f"未找到分辨率为{resolution}的下载链接: {video_id}")
                return
            video_file_name = info.get('title', video_id) + '.mp4'
        # 清理文件名
        safe_title = "".join(c for c in video_file_name if c.isalnum() or c in (' ', '_', '-', '.')).rstrip()
        filename = os.path.join(save_path, safe_title)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        if os.path.exists(filename):
            self.log(f"文件已存在，跳过: {filename}")
            return
        self.log(f"开始下载: {filename}")
        try:
            with requests.get(download_link, stream=True, timeout=self.download_timeout) as r:
                r.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            self.log(f"下载完成: {filename}")
        except Exception as e:
            self.log(f"下载失败: {e}")

    def run(self):
        email = self.get_param("username")
        password = self.get_param("password")
        video_ids_str = self.get_param("video_ids")
        save_path = self.get_param("save_path")
        resolution = self.get_param("resolution")

        if not video_ids_str:
            self.log("错误：未提供 video_ids 参数。")
            return
        video_ids = [vid.strip() for vid in video_ids_str.split(',') if vid.strip()]
        if not self.login(email, password):
            return
        self.log(f"准备下载 {len(video_ids)} 个视频...")
        for video_id in video_ids:
            info = self.get_video(video_id)
            if info:
                self.download_video(video_id, info, save_path, resolution)
            else:
                self.log(f"无法获取视频信息: {video_id}") 