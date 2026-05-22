# 业务语言规范

Creator 跟专家说话时、以及生成的目标 skill 的 SKILL.md / workflow.md / rules-and-boundaries.md 中，**必须使用业务语言**。专家不懂 AI、不懂技术实现，看到技术术语会困惑甚至放弃。

## 适用范围

| 位置 | 语言要求 |
|------|---------|
| 你对专家的每一句话 | 业务语言 |
| 目标 skill 的 SKILL.md | 业务语言 |
| 目标 skill 的 references/workflow.md | 业务语言 + 必要的流程术语 |
| 目标 skill 的 references/rules-and-boundaries.md | 业务语言 |
| 目标 skill 的 references/interview-record.md | 可含结构字段（这是机读的真值源） |
| 目标 skill 的 scripts/*.py 源码 | 技术语言（这是代码） |
| 目标 skill 的 scripts/*.py 的中文 docstring | 业务语言（解释做什么） |

## 术语黑名单（**禁止出现**在专家可见内容中）

### 一级禁忌（绝不允许）

| 技术词 | 替换表达 |
|-------|---------|
| prompt | 提示 / 指令（若必须说） |
| markdown | 文档 / 说明书 |
| frontmatter | 开头的基本信息 |
| YAML | 结构化记录 |
| schema | 格式 / 结构 |
| tokens | 字数（若必须说） |
| LLM | AI / agent |
| agent | AI 助手 / 小助手（在专家不熟悉时） |
| prompt engineering | 指令设计 |
| embeddings / vector | （避免出现） |
| fine-tuning | 定制训练（若必须说） |
| JSON / XML | 结构化数据 / 记录 |
| regex | 规则匹配 |
| API / endpoint | 接口 / 服务 |
| deploy / deployment | 上线 / 发布 |
| config / configuration | 设置 |
| environment variable | 环境配置 / 配置项 |
| stdout / stderr / stdin | （避免在用户面前出现） |
| parse / parser | 解析 / 提取信息 |
| serialize / deserialize | （避免） |
| mock | 模拟 |
| unit test / integration test | 测试 |
| commit / branch / merge | （避免 Git 术语） |
| debug / debugging | 排查 / 调整 |

### 二级词（谨慎使用）

这些词可以出现，但建议更通俗化：

| 技术词 | 更好的替换 |
|-------|-----------|
| 脚本 | 小程序 / 自动检查 |
| Python | （通常不必提语言） |
| 字段 | 信息 / 条目 |
| 解析 | 读取 / 提取 |
| 正则 | 规则 |
| 结构化 | 整理好的 |
| 对象 | 东西 / 一条记录 |

## §slug 例外（委托调用专用）

**允许**：生成的 SKILL.md / workflow.md 中**可以并必须**出现 `linkfox-xxx` 形式的 skill slug，只要该步骤的 `execution_type` 是 `delegate`。

理由：这些文件的读者是**下游 agent**（不是专家）。agent 看到 `调用 \`linkfox-sellersprite-product-search\`` 才知道该触发 Skill 工具调用子能力；写成"用卖家精灵那个工具"反而让 agent 自己瞎凑 API。

**仍不允许**：
- 你对专家说话时用 slug（专家听不懂、也不该记）——用业务名，如"卖家精灵选品"
- 在 description 的"触发：..."自然语言段里暴露 slug（description 走语义匹配，塞 slug 会污染触发判定）
- 在 interview-record.md 的 body（访谈原稿）里替专家说 slug（专家说什么就记什么）

**允许出现 slug 的具体位置**：
- SKILL.md frontmatter 的 `depends_on` 数组
- SKILL.md 正文"前置依赖"小节
- SKILL.md 正文 delegate 步骤的"调用 \`linkfox-xxx\`"句式
- workflow.md delegate 步骤的"调用 \`linkfox-xxx\`"句式
- interview-record.md frontmatter 的 `delegates_to` / `depends_on` / `delegate_search_log`

## 允许的业务术语

跨境电商领域的专业术语**可以并应该**使用：

- Listing、ASIN、SKU、MPN、UPC、EAN
- FBA、FBM、PPC、CPC、ACOS、RoAS、CTR、CR
- SEO、品牌备案、Brand Registry、A+ 页面
- Review、QA、Reviewer、Verified Purchase
- 选品、铺货、精品、Listing 优化、关键词
- 站外引流、站内广告、自动广告、手动广告
- 亚马逊、Shopee、TikTok Shop、eBay、Walmart、速卖通、Temu、Shopify、Lazada
- 类目、节点、类目节点、Category / Browse Node

这些词专家听得懂、生成的 skill 也该用。

## 具体改写示例

### 差 → 好（跟专家对话时）

| 差（有术语） | 好（业务语言） |
|-------------|---------------|
| "我会把这个内容放到 frontmatter 的 description 字段" | "我会把这个写到 skill 的基本介绍里" |
| "这一步我会用 regex 做字符串匹配" | "这一步我会用一个规则检查这段文字里有没有特定的词" |
| "我帮您生成一个 JSON schema" | "我帮您整理一个清单" |
| "这段需要做 prompt engineering" | "这段我会仔细打磨一下说法，让 AI 能更准确地执行" |
| "您的 workflow 会被 parse 成结构化数据" | "您说的流程我会整理成一步一步的清单" |

### 差 → 好（生成的 SKILL.md 正文里）

| 差 | 好 |
|----|----|
| "本 skill 用于解析 Amazon 商品页面的 HTML 并提取字段" | "这个能力帮您从 Amazon 商品详情页读取标题、品牌、描述等信息" |
| "调用脚本 parse-listing.py，输入为 URL，输出为 JSON" | "调用 `scripts/parse-listing.py`：传入商品链接，得到一份整理好的商品信息" |
| "根据 Prompt 分析描述的语义风险" | "判断描述里有没有侵权风险的措辞" |

## 脚本 docstring 的写法

脚本是技术实现，但它的 docstring（开头三引号里的说明）面向**未来要改这个脚本的人**——可能是 AI，也可能是略懂技术的专家。所以用**半技术半业务**语言：

```python
"""
品牌字段合规判定

做什么：
  判断 Amazon 商品的 brand 字段是否存在侵权风险。

输入：
  stdin JSON，格式：{"brand": "<品牌字段原文>"}

输出：
  stdout JSON，格式：{"risk_level": "red|yellow|green", "reason": "<理由>"}

不做：
  - 不判断描述措辞（那是步骤 3 的事）
  - 不调用外部接口
"""
```

**必要元素**：
- 一句话功能说明（业务语言）
- 输入 / 输出格式（给后续改代码的人看）
- "不做"清单（边界声明，帮助理解职责）

## 生成 SKILL.md 时的自检

把 SKILL.md 和 references/ 下每个 .md 都过一遍：

1. 搜 `prompt` `markdown` `frontmatter` `YAML` `schema` `tokens` `JSON` `API endpoint` `regex` — 命中任一 → 改写
2. 搜 `field` `parse` `serialize` — 命中 → 改写
3. 代码块里的内容不改（那是代码）
4. Docstring 里的结构字段名（如"输入：stdin JSON"）可以保留
5. `linkfox-xxx` 形式的 slug：仅在 §slug 例外所列位置允许；其他位置命中 → 改写为业务名

自检命中就改，别侥幸"读者可能懂"。

## 业务语言 ≠ 废话

业务语言不是"省略细节"，而是"用专家的话说精确"：

| 空话 | 精确业务语言 |
|------|-------------|
| "做得好" | "检出率 ≥ 80% 且无误杀" |
| "快速" | "5 秒内返回结果" |
| "智能" | "基于 3 条规则判断" |
| "好用" | "专家过去 10 次实操中有 9 次直接照结果提交审核" |

## 硬约束（不容商量）

- 你对专家说的每一句**绝不**出现一级禁忌词
- 目标 skill 的 SKILL.md / workflow.md / rules-and-boundaries.md 里**绝不**出现一级禁忌词
- 若必须提及技术细节，放到代码 docstring 或 scripts/ 里
- interview-record.md 的 frontmatter 字段名是机读的，**不改**；但字段的 value 值遵守上述规则
