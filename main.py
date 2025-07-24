# -*- coding: utf-8 -*-

def main():
    from core.utils import parse_cmd_args, run_workflow
    params = parse_cmd_args()
    run_workflow(params)

if __name__ == "__main__":
    main()