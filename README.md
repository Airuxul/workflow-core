# Python工作流核心框架

一个轻量级、可扩展的Python工作流执行引擎。

## 🚀 核心特性

- **模块化设计**: 每个工作流都是独立的Python类
- **可组合架构**: 工作流可以调用其他工作流作为子任务
- **分层配置**: 支持命令行参数、运行时参数和默认参数
- **参数模板**: 使用 `{{variable}}` 语法动态引用配置变量
- **全局共享上下文**: 在不同工作流间共享数据
- **触发器机制**: 支持定时、条件等多种触发方式
- **异步执行**: 支持非阻塞的异步工作流执行
- **JSON数据启动**: 通过外部JSON文件配置和启动工作流

## 🛠️ 快速开始

### 安装

```bash
# 安装 uv (如果尚未安装)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 克隆项目并安装依赖
git clone <your-repo-url>
cd workflow-core
uv sync
```

### 运行工作流

```bash
# 运行演示工作流
uv run python main.py --flow async_demo_flow

# 传递参数
uv run python main.py --flow demo_flow --param1 value1

# 通过JSON数据启动
uv run python main.py --flow_data data/workflowData/example_workflow.json
```

### JSON文件格式

创建JSON文件（如 `data/workflowData/my_workflow.json`）：

```json
{
    "flow": "demo.async_demo_flow",
    "param1": "value1",
    "param2": "value2"
}
```

## 📚 开发指南

### 创建基础工作流

```python
# workflows/my_workflow.py
from core.workflow import BaseWorkflow

class MyWorkflow(BaseWorkflow):
    DEFAULT_PARAMS = {
        "message": "Hello World",
        "count": 3
    }
    
    def run(self):
        message = self.get_param("message")
        count = self.get_param("count")
        
        for i in range(count):
            self.log(f"[{i+1}/{count}] {message}")
        
        return "工作流执行完成"
```

### 创建组合工作流

```python
from core.workflow import BaseWorkflow
from workflows.my_workflow import MyWorkflow

class ComplexWorkflow(BaseWorkflow):
    def run(self):
        # 执行子工作流
        self.run_flow(MyWorkflow, {
            "message": "来自组合工作流",
            "count": 2
        })
        
        # 设置共享值
        self.set_shared_value("last_message", "完成")
```

## 🔧 内置工作流

### 演示工作流
- **DemoSimpleExampleFlow**: 简单示例（最适合新手）
- **AsyncDemoFlow**: 异步执行演示
- **DemoParameterFlow**: 参数功能演示
- **DemoSharedContextFlow**: 共享上下文功能演示
- **DemoAsyncFlow**: 异步执行功能演示
- **DemoSystemWorkflowFlow**: 系统工作流功能演示
- **DemoTriggerFlow**: 触发器功能演示

### 系统工作流
- **BatFlow**: 执行命令行指令
- **SysVersionCheckFlow**: 系统版本检查

### 触发器工作流
- **IntervalTriggerWorkflow**: 间隔触发器

## 📁 项目结构

```
workflow-core/
├── core/                    # 核心框架代码
├── workflows/              # 工作流实现
│   ├── demo/               # 演示工作流
│   ├── system/             # 系统工作流
│   └── trigger/            # 触发器工作流
├── data/workflowData/      # JSON配置文件
├── main.py                 # 程序入口
└── pyproject.toml          # 项目配置
```

## 🧪 测试和演示

```bash
# 运行简单示例
uv run python main.py --flow demo.demo_simple_example_flow

# 运行参数演示
uv run python main.py --flow demo.demo_parameter_flow

# 运行共享上下文演示
uv run python main.py --flow demo.demo_shared_context_flow

# 运行异步处理演示
uv run python main.py --flow demo.demo_async_flow

# 运行系统工作流演示
uv run python main.py --flow demo.demo_system_workflow_flow

# 运行触发器演示
uv run python main.py --flow demo.demo_trigger_flow
```

## 📞 联系方式

- 作者: Airuxul
- 邮箱: 804754746@qq.com

祝您使用愉快！🎉 