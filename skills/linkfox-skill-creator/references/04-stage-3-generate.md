# 阶段 3：生成 skill 文件

阶段 2 通过后，你把 interview-record.md 中的结构化字段派生成一个完整的 skill 目录。本文档规定生成规则、模板引用、脚本骨架生成标准。

## 产物结构

```
skills/<target-skill-name>/
├── SKILL.md                          # 业务语言路由（≤ 200 行）
├── references/
│   ├── interview-record.md           # 结构化访谈记录（真值源，不动）
│   ├── workflow.md                   # D3 流程细化 + 对 scripts/ 的调用说明
│   └── rules-and-boundaries.md       # D4 规则 + D5 边界整合
└── scripts/                          # 仅当 D3 含至少 1 个 deterministic:true 步骤才生成
    ├── <verb>-<object>.py
    ├── ...
    └── requirements.txt              # 如有第三方依赖
```

`templates/` 下有对应骨架文件，**复制 + 填空**即可。

## SKILL.md 生成规则

### Frontmatter（必填字段）

```yaml
---
name: linkfox-<target-name>
description: "<业务描述，≥ 50 字符>。触发：<触发语 1> / <触发语 2> / <触发语 3>..."
authored_by: linkfox-skill-creator
interview_record: references/interview-record.md
quality: ready | partial | draft
depends_on: []      # 从 interview-record.md 的 depends_on 原样复制；没有 delegate 步骤则保持空数组
---
```

**description 生成规则**：
- 前半部分：用 1-2 句话说明这个 skill 做什么（业务语言）
- 后半部分：以 `触发：` 开头，列 ≥ 5 条自然语言触发词，之间用 ` / ` 分隔
- 触发词来自 D1 `typical_trigger_moment` + 专家访谈中的原话片段
- 不出现工具名、底层接口名
- 长度 50-800 字符

**quality 字段规则**：
- `ready`：D1-D5 全部有合格产出，assumed_fields 全部已确认
- `partial`：有维度被 `refused`、或专家跳过了假设确认 / 最终校对
- `draft`：skill 名是草稿名（`linkfox-draft-...`），或进度未到 `ready_to_generate`

### 正文结构（按此顺序）

```markdown
# <target-name>

<1-2 段业务语言介绍——基于 D1 的 scenario + success_criteria>

## 何时使用

<从 D1 的 typical_trigger_moment 提取>
- 场景 1
- 场景 2
- ...

## 何时不用

<从 D5 的 boundaries 提取>
- 不适用场景 1
- ...

## 核心流程

<从 D3 的 process 列表派生，每步一段>

### 步骤 1：<step.name>

<用业务语言描述这步做什么>

<按 execution_type 三选一：>
- 若 `script`：写"调用 `scripts/<script>.py`，输入是 A，输出是 B"
- 若 `llm`：用自然语言描述判断逻辑（展开 decisions 列表）
- 若 `delegate`：写"调用 `linkfox-<sub-skill-slug>` 这个 skill 完成。入参：<从 delegate_inputs_mapping 派生的业务语言清单>。输出：<业务语言>"

### 步骤 2：...

## 关键规则

<从 D4 的 rules 提取，硬规则和软规则分开展示>

### 必须遵守
- <hard rule 1>
- <hard rule 2>

### 经验性（参考，非硬性）
- <soft rule 1>
- <soft rule 2>

## 典型踩坑

<从 D5 的 pitfalls 提取>
- <pitfall 1>
- ...

## 相关资料

- `references/workflow.md` — 流程细化与脚本调用
- `references/rules-and-boundaries.md` — 完整规则与边界
- `references/interview-record.md` — 原始访谈记录
```

### 硬约束

- SKILL.md 正文 ≤ 200 行（不含 frontmatter）
- 不在正文中塞 API 参数文档（放 references/workflow.md）
- 不在 description 里暴露工具名或底层平台名（description 面向语义匹配，用业务语言）
- 用业务语言，不出现 prompt / markdown / yaml 等词（详见 `writing-style.md`）
- **例外**：`delegate` 步骤必须在正文用 `调用 \`linkfox-<sub-slug>\`` 的形式出现，让下游 agent 能触发 Skill 工具嵌套调用。slug 不算技术术语（详见 `writing-style.md` §slug 例外）

## workflow.md 生成规则

把 D3 每个步骤展开成一节，重点是"这步怎么做"：

```markdown
# 工作流程

## 流程概览

<简图：输入 → 步骤 1 → 步骤 2 → ... → 输出>

## 步骤 1：<step.name>

**输入**：<step.inputs>
**输出**：<step.outputs>
**类型**：<固定规则 / 经验判断 / 委托现成能力>

### 操作

<若 execution_type: script>
调用 `scripts/<script-name>.py`：

输入格式：
<描述>

输出格式（JSON）：
<描述>

脚本用途：<从脚本 docstring 提取>

<若 execution_type: llm>
按以下逻辑人工判断：
<展开 decisions 列表>
<保留 expert_verbatim 作为"经验参考"引用块>

<若 execution_type: delegate>
调用 `linkfox-<sub-slug>` 这个 skill 完成。

入参映射：
- <sub_skill_param_1>：<来源——D2 的哪个字段 / 专家给的常量 / 步骤 N 的输出>
- <sub_skill_param_2>：...

输出：<业务语言描述该子 skill 会返回什么，供后续步骤使用>

专家为什么选这个工具：
> <delegate_expert_quote>

### 决策点

<展开 step.decisions>

## 步骤 2：...
```

## rules-and-boundaries.md 生成规则

D4 + D5 合并整理：

```markdown
# 规则与边界

## 必须遵守的规则（硬规则）

### R1：<rule text>
- **适用范围**：<rule.scope>
- **为什么是硬规则**：<若有 expert 解释>
- **反例**：<若有>

### R2：...

## 经验性规则（软规则）

### R3：<rule text>
- **适用场景**：<scope>
- **反例**：<counter_example>
- **经验出处**：
  > <expert_verbatim>

## 不适用场景

### B1：<boundary.scenario>
**为什么不适用**：<why_not_applicable>
**专家原话**：
> <expert_verbatim>

## 典型踩坑

### P1：<pitfall.scenario>
**为什么是坑**：<why_wrong>
**专家原话**：
> <expert_verbatim>
```

## scripts/ 生成规则（核心硬约束）

### 何时生成

**当且仅当** D3 的 process 列表中存在至少 1 个 `execution_type: script` 的步骤。否则不建 `scripts/` 目录。

`execution_type: delegate` 的步骤**不生成脚本**——由下游 agent 触发对应子 skill 即可。

### 一步对应一个脚本

对每个 `execution_type: script` 的 step：

1. 文件名：`scripts/<verb>-<object>.py`
   - 从 step.name 派生，转为小写 kebab-case
   - `verb` 是动词：`check` / `parse` / `calc` / `convert` / `match` / `extract`
   - `object` 是名词：`brand-compliance` / `amazon-listing` / `profit-rate`
   - 示例：`品牌字段合规判定` → `check-brand-compliance.py`

2. 骨架：复制 `templates/script-skeleton.py.tpl`，填充：
   - 顶部中文 docstring：做什么 / 输入 / 输出 / 不做什么
   - 参数解析：从 `step.inputs` 派生命令行参数 or stdin JSON
   - 核心逻辑：能从专家口述提取明确规则的（如"brand 含 generic 标红"），直接写实现；不能提取的写 `TODO` 占位
   - 输出：JSON 打到 stdout

3. 更新对应 step 的 `script` 字段：`script: scripts/check-brand-compliance.py`

### 骨架示例（由 template 生成）

```python
#!/usr/bin/env python3
"""
品牌字段合规判定

输入：
  stdin JSON: {"brand": "<string>"}

输出：
  stdout JSON: {"risk_level": "red|yellow|green", "reason": "<string>"}

不做：
  - 不判断描述措辞是否侵权（那是步骤 3 的事，由 LLM 做）
  - 不调用外部 API
"""

import json
import sys


def classify(brand: str) -> dict:
    b = (brand or "").lower().strip()
    if "generic" in b:
        return {"risk_level": "red", "reason": "brand 含 generic"}
    # TODO: 专家说"第三方商标"也要标红，待补具体商标库
    return {"risk_level": "green", "reason": "未检出明显风险"}


def main():
    data = json.load(sys.stdin)
    result = classify(data.get("brand", ""))
    json.dump(result, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
```

### requirements.txt

- MVP 首选零依赖（只用 Python 标准库）
- 如必须用第三方包（如 `requests`、`beautifulsoup4`），写进 `scripts/requirements.txt`，每行一个包，版本号可选但建议 `>=X.Y` 形式
- 每个依赖加一行 `#` 注释说明用途
- 不引入编译慢 / 体积大的包（如 pandas、torch）除非绝对必要

## linkfox-* 工具调用与 api_call.py（上下文保护，硬约束）

### 为什么

`linkfox-*` 工具 skill（如 `linkfox-jiimore-niche-by-keyword`、`linkfox-keepa-product-history`、`linkfox-sellersprite-product-search` 等）本质都是 **API 封装**：`scripts/` 下有 1 个 `*.py` 负责发请求并把 JSON 打到 stdout。

默认的 `delegate` 模式是"用 Skill 工具嵌套调用"，下游 agent 会把子 skill 的**完整响应**回注宿主 LLM 上下文。只要返回是 10 条以上商品 / 关键词 / 评论，几轮就会撑爆上下文——宿主 skill 还没处理完就失忆。

所以：**所有 `delegate` 目标是 linkfox-* 工具 skill（纯 API 封装类）的步骤，生成时一律改用 `api_call.py` 直接执行子脚本，把 JSON 落盘到 `./data/`，宿主只看一行摘要。**

### 判定：什么算"linkfox-* 工具 skill"

满足以下**全部**条件时按工具 skill 处理：

- slug 以 `linkfox-` 开头
- 子 skill 的 `scripts/` 目录只包含 **1 个** `*.py`（且不是 `api_call.py` 本身）
- 该脚本的职责是"拿参数、调 API、打印 JSON"——没有交互式分支、没有依赖上游步骤产出

反例（这些仍走 Skill 嵌套）：业务流水线类 skill（需要 LLM 判断 / 多步组合 / 输出非结构化报告）。

### 生成规则（当 D3 至少存在一个满足上述条件的 delegate 步骤时）

1. **复制 `api_call.py` 进目标 skill 的 scripts/**：
   - 源：`templates/api_call.py`
   - 目的：`skills/<target-skill-name>/scripts/api_call.py`
   - 原样复制，不做任何改写

2. **解析子 skill 脚本路径**：
   - 默认路径模板：`~/.claude/skills/<delegates_to>/scripts/<唯一 .py 文件名>`
   - 若 `linkfoxskill skill inspect <delegates_to>` 可获取真实脚本名就用真实名；否则在 workflow.md 中以 `<TOOL_SCRIPT>` 占位并备注"首次运行前请确认路径"

3. **workflow.md 里该步骤按下面格式写调用**（**替换**掉默认的"调用 Skill 工具"段）：

   ```markdown
   ### 调用说明

   调用 `linkfox-<sub-slug>` 的底层脚本拉取数据（走 api_call.py，结果落盘，避免撑爆上下文）：

   ```bash
   python scripts/api_call.py \
     ~/.claude/skills/linkfox-<sub-slug>/scripts/<tool_script>.py \
     ./data/step<N>_<短标签>.json \
     '<JSON 参数字符串>'
   ```

   输出文件：`./data/step<N>_<短标签>.json`
   后续步骤（脚本 or LLM）按需读取该文件的**子集字段**，不要把整份 JSON 塞回上下文。
   ```

4. **顶层 `depends_on` 仍然要写**（保持和原有评估器契约兼容）：`delegates_to` 的 slug 依旧追加到 `depends_on`，即使执行路径是 api_call.py 而非 Skill 嵌套。理由：该 skill 仍是前置依赖，用户需要装它才有底层脚本。

5. **工作目录**：统一用相对路径 `./data/`（宿主 skill 运行时的当前目录）。该目录由 `api_call.py` 自动建。若宿主 skill 需要 `.tmp/` 变体（短期临时），可在 SKILL.md 顶部注明一次即可，不在每个 bash 片段里硬编码绝对路径。

6. **文件命名约定**：`step<N>_<tool_short_tag>.json`
   - N：步骤号（与 D3 process 对齐）
   - tool_short_tag：工具简称 kebab-case，如 `jiimore_niche` / `keepa_history` / `sellersprite_products`

### 示例（生成到 workflow.md）

```bash
python scripts/api_call.py \
  ~/.claude/skills/linkfox-jiimore-niche-by-keyword/scripts/jiimore_get_niche_info_by_keyword.py \
  ./data/step1c_jiimore_niche.json \
  '{"keyword":"yoga mat","countryCode":"US","sortField":"unitsSoldT7","sortType":"desc","pageSize":10}'
```

预期 stdout（一行摘要，宿主 LLM 只看这一行）：

```json
{"status":"ok","output":"/abs/path/data/step1c_jiimore_niche.json","bytes":48211,"shape":{"type":"object","top_keys":["code","data","message"],"key_count":3}}
```

### 硬禁忌

- **不在 SKILL.md 正文或 workflow.md 里教宿主 LLM 用 `Skill(linkfox-工具 slug)` 嵌套调用**。此类 slug 一律走 api_call.py。
- **不把落盘 JSON 直接读进宿主 LLM 当上下文**。宿主只处理摘要或通过下一步脚本解析；真要 LLM 看内容，也必须先用脚本裁剪到前 N 条 / 关键字段。
- **不在 api_call.py 里加入 API Key 相关逻辑**。Key 由底层工具脚本自己读环境变量，api_call.py 只做进程调度与落盘。
- **不在生成时修改 api_call.py 的内容**。所有 skill 共用同一份，评估器据此校验签名一致性。

## 委托依赖处理（delegate 步骤）

若 D3 中存在 `execution_type: delegate` 步骤：

1. 该步骤的 `delegates_to` 值汇总到顶层 `depends_on` 数组（去重），同步写入 SKILL.md 的 frontmatter
2. SKILL.md 的"何时使用"后加一节"前置依赖"，列出每个依赖 skill 的业务名与用途：

   ```markdown
   ## 前置依赖

   本能力需要以下现成小助手配合才能完整运行：

   - `linkfox-sellersprite-product-search` — 卖家精灵选品（用于按条件拉取竞品数据）
   - `linkfox-keepa-product-history` — Keepa 历史价格（用于补充价格曲线）

   首次使用前请确认这些小助手已安装（可通过 `linkfoxskill search` 搜索）。
   ```
3. workflow.md 对应步骤按上文的 delegate 分支模板写入
4. **不生成脚本**——delegate 步骤的执行交给下游 agent 通过 Skill 工具嵌套调用完成

## D7 外部依赖处理（仅 script 步骤）

若 D3 中有 `execution_type: script` 步骤需要调平台 API 或第三方服务（delegate 搜索无结果、专家确认自写）：

1. 请求封装写到 `scripts/<verb>-<service>.py`（如 `fetch-amazon-listing.py`）
2. 认证信息用环境变量，**不写死在脚本里**
3. 在脚本 docstring 顶部注明需要的环境变量（`Requires env: LINKFOX_API_KEY`）
4. SKILL.md 的"何时使用"后加一节"使用前置"，列出需要的环境变量

## 生成顺序（严格）

1. 创建目录：`skills/<name>/`、`skills/<name>/references/`
2. 写 interview-record.md（把结构化字段定稿 + 访谈原稿归档）
3. 写 SKILL.md（按模板 + 填充）
4. 写 workflow.md
5. 写 rules-and-boundaries.md
6. 若需脚本：创建 `scripts/`，逐个生成 .py；如有依赖再建 `requirements.txt`
7. **若存在任一 linkfox-* 工具 delegate 步骤**：把 `templates/api_call.py` 原样复制到 `scripts/api_call.py`（未建 `scripts/` 时先建）
8. **自检**：跑 `linkfoxskill skill lint <name>`（或等价的 10 项契约检查），全绿或仅剩警告再进阶段 4
9. 写进度：`<!-- interview-progress: ... status=complete -->`

## 自检（生成完跑一遍）

- [ ] SKILL.md 正文行数 ≤ 200
- [ ] description 长度 ≥ 50 字符、含 `触发：`
- [ ] `authored_by: linkfox-skill-creator` 存在
- [ ] `interview_record: references/interview-record.md` 指向的文件存在
- [ ] 每个 `execution_type: script` 步骤的 `script` 指向的 .py 文件存在
- [ ] 每个 .py 脚本有非空 docstring
- [ ] 若有 requirements.txt，格式可被 pip 解析
- [ ] SKILL.md 和 references/*.md 中不出现 `prompt` / `frontmatter` / `tokens` / `yaml` / `schema` 等技术词（skill slug 例外）
- [ ] 每个 `execution_type: delegate` 步骤的 `delegates_to` 值出现在顶层 `depends_on` 数组中
- [ ] 顶层 `depends_on` 每一条都能在 `delegate_search_log` 找到对应的 `expert_choice` 记录（专家确认证据）
- [ ] SKILL.md "前置依赖"一节列齐了 `depends_on` 中的每个 skill
- [ ] 步骤描述中如出现已知平台关键词（卖家精灵 / Keepa / ABA / Helium10 / Jiimore / Ruiguan / Zhihuiya 等）→ 该步 `execution_type` 必须是 `delegate`，或 `delegate_search_log` 中有该步骤的搜索记录且专家拒绝
- [ ] 所有 `depends_on` 中的 slug 本地或云端可解析（通过 `linkfoxskill search <slug>` 能找到；找不到的在交接话术里明确提醒专家发布前需确保可安装）
- [ ] 若 `depends_on` 中存在任一 linkfox-* 工具 skill → `scripts/api_call.py` 存在，且内容与 `templates/api_call.py` 字节一致
- [ ] 所有 linkfox-* 工具 delegate 步骤在 workflow.md 中都写成 `python scripts/api_call.py ...` 形式，落盘路径以 `./data/step<N>_` 开头
- [ ] SKILL.md 和 workflow.md 中不出现 `Skill(linkfox-` 或"调用 Skill 工具嵌套执行 linkfox-" 等措辞（工具类 delegate 必须走 api_call.py）

若自检有 error，修复后重跑；有 warning 可先进阶段 4，但在交接话术里告诉专家"有这些小问题，可以后面再优化"。

## 硬禁忌

- 不擅自发明专家没说过的规则 / 步骤 / 边界
- 不改写 `expert_verbatim` 字段
- 不在 `execution_type: llm` 的步骤写脚本（专家说过"靠经验"就是靠下游 agent 语言理解）
- 不在 scripts 里塞环境变量默认值为真实 key
- 不把 SKILL.md 写超 200 行——超了就往 references 里挪
- **不在 `depends_on` 中添加未经专家确认的 skill**（即使你觉得那个 skill 更合适）
- **不把 `execution_type: delegate` 的步骤写成脚本**（那样下游 agent 就不会触发子 skill 了）
