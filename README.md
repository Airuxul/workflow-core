# Python工作流框架

这是一个轻量级、可扩展的Python工作流执行引擎。它允许用户通过定义独立的、可组合的工作流类来编排复杂的任务。

## 核心特性

- **模块化**: 每个工作流都是一个独立的Python类，易于管理和复用。
- **可组合**: 一个工作流可以调用其他工作流作为子任务，构建复杂的执行逻辑。
- **分层配置**: 支持命令行参数、工作流运行时参数和工作流默认参数，上层参数可自动传递给子工作流。
- **参数模板**: 在参数值中可以使用 `{{variable}}` 语法动态引用其他配置变量。
- **全局共享上下文**: 允许在不同工作流的执行过程中共享数据，通过`set_shared_value`函数进行设置。
- **循环依赖检测**: 自动检测并阻止工作流之间的循环调用，防止无限递归。

## 环境要求

- Python >= 3.8
- [uv](https://docs.astral.sh/uv/) (推荐的包管理工具)

## 安装和设置

### 1. 安装 uv (如果尚未安装)

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 克隆项目并安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd workflow-core

# 使用 uv 安装依赖（会自动创建虚拟环境）
uv sync
```

## 如何运行

使用 uv 运行工作流引擎。通过 `--flow` 参数指定要执行的入口工作流的名称（类名，使用蛇形命名法）。

**示例：**

运行项目内置的主测试流程：
```bash
uv run python main.py --flow main_test_flow
```

运行壁纸视频复制流程：
```bash
uv run python main.py --flow wallpaper_video_copy_flow
```

运行Iwara下载流程：
```bash
uv run python main.py --flow iwara_download_flow
```

## 依赖管理

### 添加新依赖
```bash
uv add package_name
```

### 添加开发依赖
```bash
uv add --dev package_name
```

### 更新依赖
```bash
uv sync
```

### 查看已安装的包
```bash
uv pip list
```

## 如何创建新的工作流

1. 在 `workflows` 目录下创建一个新的Python文件（例如 `my_new_flow.py`）。
2. 在该文件中，创建一个继承自 `core.workflow.BaseWorkflow` 的类。
3. 实现 `run(self)` 方法，将你的业务逻辑放在这里。
4. 如果需要，可以定义一个 `DEFAULT_PARAMS` 字典来为当前工作流提供默认参数。

## 项目结构

```
workflow-core/
├── core/                    # 核心框架代码
│   ├── config.py           # 配置管理
│   ├── constants.py        # 常量定义
│   ├── manager.py          # 工作流管理器
│   ├── utils.py            # 工具函数
│   └── workflow.py         # 基础工作流类
├── workflows/              # 工作流实现
│   ├── wallpaper_video_copy_flow.py    # 壁纸视频复制
│   ├── iwara_download_flow.py          # Iwara视频下载
│   └── ...                 # 其他工作流
├── main.py                 # 程序入口
├── pyproject.toml          # uv项目配置和依赖
└── README.md               # 项目说明
```