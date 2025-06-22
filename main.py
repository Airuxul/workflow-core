# -*- coding: utf-8 -*-

import argparse
from core.utils import parse_extra_args, run_workflow

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

    run_workflow(args.flow_name, cli_params)

if __name__ == "__main__":
    main()