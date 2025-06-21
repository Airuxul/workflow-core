# -*- coding: utf-8 -*-

import argparse
from core.manager import WorkflowManager
from core.utils import find_workflow_class, parse_extra_args

def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="工作流执行引擎")
    parser.add_argument(
        "--flow",
        dest="flow_name",
        required=True,
        help="要执行的主工作流名称 (例如: main_test_flow)"
    )
    
    args, unknown = parser.parse_known_args()
    
    cli_params = parse_extra_args(unknown)

    try:
        # 1. 查找主工作流类
        main_workflow_class = find_workflow_class(args.flow_name)
        
        # 2. 初始化管理器
        manager = WorkflowManager(cli_params=cli_params)
        
        # 3. 运行主工作流
        manager.run_flow(workflow_class=main_workflow_class)

    except (FileNotFoundError, AttributeError) as e:
        print(f"错误: {e}")
    except Exception as e:
        print(f"发生致命错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()