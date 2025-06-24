# -*- coding: utf-8 -*-

import os
import requests
import hashlib
from requests.auth import AuthBase
from core.workflow import BaseWorkflow
from core import constants
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
from requests.exceptions import ChunkedEncodingError, HTTPError, SSLError
from http.client import IncompleteRead
import random

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
        "resolution": "Source", # 下载分辨率 (例如: Source, 1080p, 720p, 540p, 360p)
        "thread_num": 4        # 下载线程数，默认4
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

    def tqdm_log(self, msg):
        """带缩进的 tqdm 日志输出，保证风格统一。"""
        tqdm.write(f"{self.get_log_indent()}{msg}")

    def download_video(self, video_id, info, save_path, resolution, pbar=None):
        # 兼容 fileUrl 直链和资源列表
        if 'fileUrl' in info:
            url = info['fileUrl']
            file_id = info['file']['id']
            expires = url.split('/')[4].split('?')[1].split('&')[0].split('=')[1]
            SHA_postfix = "_5nFp9kmbNnHdAFhaqMvt"
            SHA_key = file_id + "_" + expires + SHA_postfix
            hash_val = hashlib.sha1(SHA_key.encode('utf-8')).hexdigest()
            headers_api = {"X-Version": hash_val}
            resources = requests.get(url, headers=headers_api, auth=BearerAuth(self.token), timeout=self.timeout).json()
            # 选择分辨率
            resource = None
            for res in resources:
                if res['name'] == resolution:
                    resource = res
                    break
            if not resource:
                self.tqdm_log(f"未找到分辨率为{resolution}的下载链接: {video_id}")
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
                self.tqdm_log(f"未找到分辨率为{resolution}的下载链接: {video_id}")
                return
            video_file_name = info.get('title', video_id) + '.mp4'
        
        # 清理文件名
        safe_title = "".join(c for c in video_file_name if c.isalnum() or c in (' ', '_', '-', '.')).rstrip()
        # 进度条 desc 过长时省略号截断
        max_desc_len = 32
        if len(safe_title) > max_desc_len:
            safe_title = safe_title[:max_desc_len - 3] + '...'
        filename = os.path.join(save_path, safe_title)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        max_retries = 3
        chunk_size = 128 * 1024  # 128KB，减少请求次数
        for attempt in range(max_retries):
            try:
                # 断点续传逻辑
                temp_file = filename + ".part"
                mode = 'ab'  # 追加写
                downloaded = 0
                if os.path.exists(temp_file):
                    downloaded = os.path.getsize(temp_file)
                headers = {}
                if downloaded > 0:
                    headers['Range'] = f'bytes={downloaded}-'
                with requests.get(download_link, stream=True, timeout=self.download_timeout, headers=headers) as r:
                    try:
                        r.raise_for_status()
                    except HTTPError as e:
                        if r.status_code == 416:
                            # 断点文件超出范围，自动删除并重试
                            if os.path.exists(temp_file):
                                os.remove(temp_file)
                            self.tqdm_log(f"检测到 416 错误，已删除断点文件，准备重新下载: {filename}")
                            continue  # 进入下一次重试
                        else:
                            raise
                    total = int(r.headers.get('content-length', 0))
                    # 计算总大小
                    if 'Content-Range' in r.headers:
                        # 服务器支持断点续传
                        total = int(r.headers['Content-Range'].split('/')[-1])
                    if pbar is not None:
                        pbar.reset(total=total)
                        pbar.n = downloaded
                        pbar.last_print_n = downloaded
                        pbar.refresh()
                    with open(temp_file, mode) as f:
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                if pbar is not None:
                                    pbar.update(len(chunk))
                # 下载完成后重命名
                os.rename(temp_file, filename)
                self.tqdm_log(f"下载完成: {filename}")
                break  # 成功则跳出重试循环
            except IncompleteRead as e:
                self.tqdm_log(f"下载失败: IncompleteRead {e} (第{attempt+1}次尝试)")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    self.tqdm_log(f"多次重试后仍失败: {filename}")
            except ChunkedEncodingError as e:
                self.tqdm_log(f"下载失败: ChunkedEncodingError {e} (第{attempt+1}次尝试)")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    self.tqdm_log(f"多次重试后仍失败: {filename}")
            except SSLError as e:
                self.tqdm_log(f"下载失败: SSLError {e} (第{attempt+1}次尝试)")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    self.tqdm_log(f"多次重试后仍失败: {filename}")
            except Exception as e:
                self.tqdm_log(f"下载失败: {e} (第{attempt+1}次尝试)")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    self.tqdm_log(f"多次重试后仍失败: {filename}")

    def get_log_indent(self):
        """获取当前工作流的缩进字符串，便于日志和进度条统一风格。"""
        return '\t' * (self.manager.flow_depth if getattr(self.manager, 'flow_depth', 0) > 0 else 0)

    def run(self):
        email = self.get_param("username")
        password = self.get_param("password")
        video_ids_str = self.get_param("video_ids")
        save_path = self.get_param("save_path")
        resolution = self.get_param("resolution")
        thread_num = int(self.get_param("thread_num"))

        if not video_ids_str:
            self.log("错误：未提供 video_ids 参数。")
            return
        video_ids = [vid.strip() for vid in video_ids_str.split(',') if vid.strip()]
        if not self.login(email, password):
            return
        self.log(f"准备下载 {len(video_ids)} 个视频... (线程数: {thread_num})")
        
        # 预先获取所有视频信息
        video_infos = {}
        for vid in video_ids:
            info = self.get_video(vid)
            video_infos[vid] = info

        # 创建 tqdm 进度条
        progress_bars = {}
        indent = self.get_log_indent()
        failed_ids = []  # 新增：记录失败的视频id
        for idx, vid in enumerate(video_ids):
            info = video_infos[vid]
            if info is None:
                failed_ids.append(vid)
                continue
            # 先尝试获取文件大小
            file_size = 0
            if 'fileUrl' in info:
                url = info['fileUrl']
                file_id = info['file']['id']
                expires = url.split('/')[4].split('?')[1].split('&')[0].split('=')[1]
                SHA_postfix = "_5nFp9kmbNnHdAFhaqMvt"
                SHA_key = file_id + "_" + expires + SHA_postfix
                hash_val = hashlib.sha1(SHA_key.encode('utf-8')).hexdigest()
                headers = {"X-Version": hash_val}
                resources = requests.get(url, headers=headers, auth=BearerAuth(self.token), timeout=self.timeout).json()
                resource = None
                for res in resources:
                    if res['name'] == resolution:
                        resource = res
                        break
                if resource and 'size' in resource['src']:
                    file_size = int(resource['src']['size'])
                # 获取文件名
                file_type = resource['type'].split('/')[1] if resource else 'mp4'
                video_file_name = info.get('title', vid) + '.' + file_type
            else:
                files = info.get('files', [])
                for file in files:
                    if file.get('resolution') == resolution:
                        file_size = file.get('size', 0)
                        break
                video_file_name = info.get('title', vid) + '.mp4'
            safe_title = "".join(c for c in video_file_name if c.isalnum() or c in (' ', '_', '-', '.')).rstrip()
            # 进度条 desc 过长时省略号截断
            max_desc_len = 32
            if len(safe_title) > max_desc_len:
                safe_title = safe_title[:max_desc_len - 3] + '...'
            desc = f"{indent}{safe_title}"
            progress_bars[vid] = tqdm(total=file_size, desc=desc, position=idx, unit='B', unit_scale=True, unit_divisor=1024, leave=True, dynamic_ncols=True, mininterval=0.5, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]')

        def download_task(video_id, info, pbar):
            time.sleep(random.uniform(0.5, 1))  # 随机延迟，避免高并发
            try:
                self.download_video(video_id, info, save_path, resolution, pbar)
            except Exception:
                failed_ids.append(video_id)

        with ThreadPoolExecutor(max_workers=thread_num) as executor:
            futures = [
                executor.submit(download_task, vid, video_infos[vid], progress_bars[vid])
                for vid in video_ids if video_infos[vid] is not None
            ]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.log(f"线程任务异常: {e}")
        for pbar in progress_bars.values():
            pbar.close()
        print() # 输出空行，避免串行
        if failed_ids:
            self.tqdm_log(f"下载失败的视频id: {', '.join(failed_ids)}")
        else:
            self.tqdm_log("所有视频下载成功！") 