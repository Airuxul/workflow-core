# -*- coding: utf-8 -*-

from core.utils import run_workflow

# python -m test\test_wallpaper_video_copy_flow

def debug_main():
    # 直接在这里填写要调试的参数
    flow_name = "wallpaper_video_copy_flow"  # 例如: main_test_flow 或 iwara_download_flow
    run_workflow(flow_name, {})

if __name__ == "__main__":
    debug_main()