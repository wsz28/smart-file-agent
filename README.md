# 智能文件整理 Agent（smart-file-agent）

把"下载目录越堆越乱、人工分类慢"的日常痛点，抽象为 **扫描 → 分类决策 → 归档 → 报告** 四步流程的自动化整理工具。**纯 Python 标准库、零依赖、跨平台**。

## 功能特性

- **三级分类策略，逐级兜底**：
  1. 文本内容关键词识别（票据 / 合同等）
  2. 扩展名规则（`rules.json`）
  3. 可选大模型裁决（接入任意 OpenAI 兼容 API，可插拔）
- **安全与容错**：
  - 默认 **dry-run** 只预览、不操作
  - **只移动、不删除**，重名自动加序号，绝不覆盖
  - 全过程写日志，并生成 **Markdown 整理报告**
- **工程化**：纯标准库、零依赖；分类规则**外置为 JSON**，改规则不用改代码

## 工作流程

```
扫描源目录 ──> 三级分类决策 ──> 归档(dry-run/apply) ──> Markdown 报告 + 日志
    │            │
    │            ├─ 关键词 → 扩展名 → 大模型(可选)
    └─ 跳过隐藏/垃圾文件
```

## 目录结构

```
smart-file-agent/
├── agent/
│   ├── scanner.py       # 扫描目录，收集待整理文件
│   ├── classifier.py    # 三级分类策略（关键词/扩展名/大模型）
│   ├── mover.py         # 归档（dry-run、只移动、重名加序号）
│   ├── reporter.py      # Markdown 报告 + 日志
│   └── llm.py           # 可选大模型裁决接口（可插拔）
├── rules.json           # 分类规则（外置，改规则不改代码）
└── run.py               # 主入口
```

## 快速开始

```bash
# 1. 扫描并预览（默认 dry-run，什么都不动）
python run.py --src ./downloads

# 2. 真正执行整理
python run.py --src ./downloads --apply

# 3. 开启可选大模型裁决（需设置 LLM_API_KEY）
python run.py --src ./downloads --apply --llm
```

参数说明：

| 参数 | 说明 | 默认 |
|---|---|---|
| `--src` | 待整理源目录 | `downloads` |
| `--dest` | 归档目标根目录 | `sorted` |
| `--rules` | 分类规则 JSON | `rules.json` |
| `--log` | 日志文件 | `agent.log` |
| `--report` | Markdown 报告路径 | `report.md` |
| `--apply` | 真正移动（默认 dry-run） | off |
| `--llm` | 启用大模型裁决 | off |

## 定制分类规则

编辑 `rules.json` 即可增删分类，无需改代码。每个分类支持 `keywords`（文本关键词）和 `extensions`（扩展名），优先级：关键词 > 扩展名 > 大模型。

```json
{
  "categories": [
    { "name": "发票", "keywords": ["发票", "invoice"], "extensions": [".pdf", ".png"] }
  ],
  "default_category": "未分类"
}
```

## 可选大模型裁决

设置以下环境变量即可启用第 3 级裁决（未配置时自动跳过，保持零依赖）：

```bash
set LLM_API_KEY=your_key
set LLM_BASE_URL=https://api.deepseek.com/v1
set LLM_MODEL=deepseek-chat
```

## 作者

wsz28 · 人工智能专业
