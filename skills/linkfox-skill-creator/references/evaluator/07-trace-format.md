# 07 轨迹格式契约

E4 的子 agent C 和 D 必须按本文档定义的格式输出执行轨迹。格式不合规 → `trace_parseability: partial/fail` → behavior_score 下调。

## 文件位置

轨迹归档于：

```
{skill_dir}/.eval/trace-{YYYYMMDD-HHmm}.md
```

一次 E4 跑一个 trace 文件，文件内含：

- 合成任务部分（1 次 spawn 的轨迹）
- 反例集部分（N 次 spawn 的轨迹，每次一段）

## 每步一个 trace:step 块

子 agent 每执行一个 step，在响应中插入一个 HTML 注释包裹的块：

```
<!-- trace:step -->
STEP: step_2
NAME: 品牌关键词扫描
INPUT:
  - title: "Wireless Bluetooth Earbuds Compatible with AirPods Pro"
  - brand: "SonyBeats"
ACTION: 调用 scripts/check-brand-keywords.py，参数 {title, brand}
SCRIPT_USED: true
OUTPUT:
  - brand_match: AirPods 命中品牌库
  - hit_keywords: [AirPods]
RULES_CHECKED: [R3, R7]
```

### 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| STEP | string | 是 | 必须匹配 process.md 中定义的 step id（如 `step_2`） |
| NAME | string | 否 | 可读名称，便于调试 |
| INPUT | yaml list | 是 | 本步的输入（可以是 key-value 对的列表） |
| ACTION | string | 是 | 本步实际做了什么。若调了脚本，明写脚本路径和参数 |
| SCRIPT_USED | boolean | 是 | 是否真调用了 `scripts/*.py`（而非 LLM 自己算）。**deterministic step 必须为 true** |
| OUTPUT | yaml list | 是 | 本步的输出 |
| RULES_CHECKED | list of string | 是 | 本步参考或检查了哪些 rule id |

## 会话末尾 summary 块

子 agent 执行完所有步骤后，输出一个 JSON 汇总：

```json
<!-- trace:summary -->
{
  "task_id": "synthetic-main",
  "steps": [
    {
      "step": "step_1",
      "name": "输入校验",
      "script_used": false,
      "rules_checked": []
    },
    {
      "step": "step_2",
      "name": "品牌关键词扫描",
      "script_used": true,
      "script_path": "scripts/check-brand-keywords.py",
      "rules_checked": ["R3", "R7"]
    }
  ],
  "total_duration_ms": 45000,
  "completed": true,
  "final_output": "疑似蹭 AirPods 品牌，建议修改"
}
```

### summary 字段

| 字段 | 说明 |
|------|------|
| task_id | synthetic-main / ce-1 / ce-2 ... 用于在报告中对应 |
| steps | list of 简化版 step，字段 = STEP + SCRIPT_USED + RULES_CHECKED |
| total_duration_ms | 可选，有则记录 |
| completed | true = 流程跑完；false = 被迫中断（超时 / 错误） |
| final_output | 一句话总结最终给用户的答案 |

## 反例集的轨迹格式

每条反例单独一组 `trace:step` + `trace:summary`，且在文件中用一个 H2 标题分隔：

```markdown
## 合成任务

<!-- trace:step --> ...
<!-- trace:step --> ...
<!-- trace:summary --> {...}

## 反例 CE-1：FDA Registered 虚假声明

<!-- trace:step --> ...
<!-- trace:summary --> {...}

## 反例 CE-2：Shopify 平台不适用

<!-- trace:step --> ...
<!-- trace:summary --> {...}
```

## 解析

主评估 agent 用以下正则粗解析：

- trace:step 块：从 `<!-- trace:step -->` 起到下一个 `<!-- trace:(step|summary) -->` 之间（或下一个 H2）
- trace:summary 块：`<!-- trace:summary -->\s*(?:```json\s*)?(\{[\s\S]*?\})(?:\s*```)?`
- 按 H2 分段区分合成任务与各反例

**如果子 agent 没输出 JSON 格式的 summary** —— 主 agent 尝试从 trace:step 块聚合等价信息（手动构造 steps 列表）。能聚合出来 → `trace_parseability: degraded`；聚合失败 → `trace_parseability: fail`，behavior_score 按能算出的部分子分算，不能算的子分置 N/A。

## 子 agent 的 prompt 约定

spawn C/D 时，prompt 末尾必须包含这段模板（原文）：

```
输出约定：
- 每执行一个步骤，输出一个 <!-- trace:step --> 块，包含 STEP / NAME / INPUT / ACTION / SCRIPT_USED / OUTPUT / RULES_CHECKED
- STEP 字段必须匹配 skill references/workflow.md 中的 step id
- deterministic 步骤必须真调 scripts/*.py（Bash 工具），SCRIPT_USED=true
- 所有步骤结束后，输出一个 <!-- trace:summary --> 块（JSON），包含 task_id / steps / completed / final_output
- 轨迹块用于评估，不会影响你回答用户的最终结果
```

## SCRIPT_USED 的双源核对

- 主来源：trace 里自报的 `SCRIPT_USED: true`
- 次来源：主评估 agent 能拿到的子 agent Bash 工具调用记录（Claude Code Agent 工具返回的 transcript）

若两源矛盾：

- 自报 true + Bash 无 python 调用 → 标 `bypass_reason: "自报 true 但无实际调用记录"`
- 自报 false + Bash 有 python 调用 → 信 Bash（算 true），标 `note: "self-reported false but actually invoked"`

双源都无法确认时（如子 agent 工具日志不可用）：仅用自报，报告 `script_verification: self_reported_only`。

## 示例：完整一次 E4 的 trace 文件

```markdown
# trace-20260427-1530.md

## 合成任务

<!-- trace:step -->
STEP: step_1
NAME: 输入校验
INPUT:
  - title: "..."
  - brand: "..."
ACTION: 检查必填字段是否齐全
SCRIPT_USED: false
OUTPUT:
  - validated: true
RULES_CHECKED: []

<!-- trace:step -->
STEP: step_2
NAME: 品牌关键词扫描
INPUT:
  - title: "..."
  - brand: "..."
ACTION: python scripts/check-brand-keywords.py <<< '{"title": "...", "brand": "..."}'
SCRIPT_USED: true
OUTPUT:
  - brand_match: true
  - hit_keywords: [AirPods]
RULES_CHECKED: [R3]

<!-- trace:summary -->
{
  "task_id": "synthetic-main",
  "steps": [
    { "step": "step_1", "script_used": false, "rules_checked": [] },
    { "step": "step_2", "script_used": true, "script_path": "scripts/check-brand-keywords.py", "rules_checked": ["R3"] }
  ],
  "completed": true,
  "final_output": "疑似蹭 AirPods"
}

## 反例 CE-1：...
...
```
