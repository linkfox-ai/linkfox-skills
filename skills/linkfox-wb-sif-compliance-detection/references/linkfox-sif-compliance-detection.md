# linkfox-sif-compliance-detection 参考

## 功能与边界

该业务能力通过商品图片检索外观登记相似候选。它返回来源登记标识、匹配证据、分类、法律状态提示、覆盖信息和警告，供产品外观风险候选排查使用。结果不构成侵权判定、有效性结论、自由实施意见或其他法律意见。

不处理专利全文、商标或 TRO 检测、卖家账号、商品搜索、采购履约或其他平台运营事务。没有图片时不调用；空结果、覆盖失败和服务错误都不能解释为没有风险。

## MCP 路由

- 原 endpoint：`/ecDw/designSimilarSearch`
- 精确 `toolName`：`ecDw/designSimilarSearch`
- MCP 调用：`LinkFox.proxy_call`
- 参数位置：业务 JSON 对象直接放在 `arguments`，不套 `body`、`params`、`data` 或第二层 `arguments`
- 本地图片：可将图片字节编码为纯 Base64 后放入 `imageBase64`，不需要文件上传能力

## 请求参数

| 参数 | 类型 | 必填 | 约束与含义 |
|---|---|---|---|
| `imageUrl` | string | 与 `imageBase64` 二选一 | 公网 HTTP(S) 图片地址，建议 8–4096 字符，不应包含 URL 凭据 |
| `imageBase64` | string | 与 `imageUrl` 二选一 | 图片字节的纯 Base64，不含 `data:image/...;base64,` 前缀，长度约束为 16–12582912 个编码字符 |
| `title` | string | 否 | 辅助图片语义，1–4096 字符；不能替代图片，图像与文本分数不相加 |
| `topK` | integer | 否 | 默认 20，范围 1–200；候选上限不是用户费用单位 |
| `regions` | string[] | 否 | 最多 64 个不重复的两字母 ISO-2 地区码，例如 `CN`、`US`、`EM`；欧洲范围在此使用 `EM` |
| `jurisdictionCodes` | string[] | 否 | 最多 32 个不重复的来源归属码，例如 `USID`、`EMID`；不是 ISO-2 地区码 |
| `topLoc` | string[] | 否 | 最多 32 个不重复的两位数字洛迦诺主分类前缀，例如 `09`、`22` |
| `locarnoClasses` | string[] | 否 | 洛迦诺完整分类码，例如 `22-06`，保留字符串和前导零 |
| `patentStatus` | integer[] | 否 | 只能是 `[0]`、`[1]` 或 `[0,1]`，分别表示失效、有效或两者；省略表示不预设状态偏好 |

`imageUrl` 与 `imageBase64` 必须且只能提供一个。文本字段不能有首尾空白，筛选数组不得包含 null 或重复项。可选字段不用时优先省略，不要使用空字符串、数字字符串或逗号拼接字符串替代数组。`regions` 和 `jurisdictionCodes` 同时提供时取交集；不要把来源归属码当成 ISO-2 地区码。缺分类候选和 unknown 或 pending 法律状态由来源规则处理，Agent 不得自行删除或重筛。

## 响应 envelope

成功应同时检查 MCP 调用没有外层错误、业务 `errcode` 为 `200`，以及上游 `data.code` 为 `OK`。主要业务结果位于 `data.data`，候选位于 `data.data.candidates`。

| 路径 | 类型 | 用途 |
|---|---|---|
| `errcode`, `errmsg` | integer, string | 业务层状态和消息，成功为 `200` |
| `data.code`, `data.message` | string | 上游状态和消息，成功 code 为 `OK` |
| `data.request_id`, `upstreamRequestId` | string | 请求追踪标识，按实际返回展示 |
| `data.data.candidates` | object[] | 外观登记候选，空列表不代表没有风险 |
| `data.data.coverage` | object | 来源覆盖与元数据完整性 |
| `data.data.warnings` | string[] | 来源警告，原样保留 |
| `data.data.capability_version` | string | 来源能力或规则版本，不硬编码 |
| `data.data.asset_code`, `data.data.asset` | string | 来源资产标识，按实际返回展示 |
| `data.data.model_versions` | object | image、text 等模态模型版本，仅展示返回项 |
| `data.data.execution` | object | 来源执行和调试元数据，通常只在排障时展示 |
| `data.data.category_filter` | object | 来源分类筛选元数据 |
| `data.data.risk_adjustment` | object | 来源风险调整元数据 |
| `data.data.line_rerank` | object | 来源线图重排元数据，可能缺省 |
| `data.usage` | object | 来源账户用量，不是用户 LinkFox 余额或用户售价 |
| `costToken`, `costCredit` | integer | 实际返回的费用字段，缺失不等于免费 |

公共序列化可能省略 null 字段。缺省和 null 都按来源事实未知处理，不承诺每次返回完整字段集合。text 内容若承载 JSON，只解析一次，再按上述路径读取；不要把 MCP 外层对象直接当作业务 envelope。

## 候选字段

以下字段均以 `data.data.candidates[]` 为父路径，可能缺省或为 null。日期按来源的 `YYYY-MM-DD` 字符串展示。

| 字段 | 类型 | 说明 |
|---|---|---|
| `design_registration_id` | string | 来源外观登记唯一标识 |
| `primary_identifier` | string | 来源主要检索标识 |
| `application_number` | string | 申请号 |
| `registration_number` | string | 登记号 |
| `publication_number` | string | 公布号 |
| `registration_jurisdiction_code` | string | 来源归属码，如 `EMID` 或 `USID` |
| `jurisdiction_iso2` | string | 来源 ISO-2 地区字段，不与归属码互换 |
| `title` | string | 原始标题 |
| `title_en` | string | 来源英文标题，不自行翻译 |
| `title_language` | string | 原始标题语言 |
| `title_en_source` | string | 英文标题来源 |
| `holder_names` | string[] | 持有人信息 |
| `designer_names` | string[] | 设计人信息 |
| `locarno_classes` | string[] | 来源洛迦诺分类 |
| `image_score` | number | 原始图像模态分数 |
| `text_score` | number | 原始文本模态分数，与 `image_score` 不相加 |
| `similarity` | number | 来源 0–100 相似度，不是概率，不再乘以 100 |
| `matched_modality` | string | 本候选命中的模态 |
| `simple_legal_status` | string | 来源法律状态，不自行推断 |
| `registration_date` | string | 登记日期 |
| `application_date` | string | 申请日期 |
| `publication_date` | string | 公布日期 |
| `image_available` | boolean | 图片可用提示，不等于图片 URL |
| `risk_level` | string | 来源规则层风险提示，不构成侵权判定 |
| `risk_reasons` | string[] | 来源规则依据，空数组也不等于无风险 |

## coverage 与处理元数据

`data.data.coverage` 可能包含以下字段，来源可缺省、增加或返回 null。

| 字段 | 说明 |
|---|---|
| `candidate_total`, `indexed_vectors` | 来源候选单位总数和已索引向量数，不等于本次返回数量 |
| `candidate_unit`, `collection_name` | 来源计数单位和集合标识 |
| `coverage_ratio` | 来源定义的比值，可能大于 1，不能解释为 0–1 概率或完整覆盖百分比 |
| `unresolved_hits`, `unverified_hits_dropped` | 未解析命中数和未经核实而丢弃的命中数 |
| `metadata_unknown` | holder、legal_status、locarno_class 等未知元数据计数，不是逐候选判定 |
| `modalities` | image 或 text 等模态的覆盖对象和计数 |

来源处理信息可能包含 `execution.engine`、`execution.elapsed_ms`、`execution.timings_ms`、`category_filter.applied`、`category_filter.dropped`、`category_filter.anchor_classes`、`category_filter.query_ref_classes`、`risk_adjustment.applied`、`risk_adjustment.version`、`risk_adjustment.same_design_capped`、`risk_adjustment.category_unknown`、`risk_adjustment.cross_category`、`line_rerank.applied`、`line_rerank.reranked`、`line_rerank.max_candidates`、`line_rerank.media_missing` 和 `line_rerank.weight`。这些是来源元数据，不要自行重新加权、重排或解释为额外法律结论。

`data.usage` 可能包含 `record_id`、`request_units`、`credit_cost`、`credit_waived`、`remaining_quota`、`remaining_credits` 和 `credit_breakdown`。这些字段描述来源账户用量，不能展示为用户 LinkFox 余额或用户应付金额。用户费用只按实际返回的费用字段展示。

## 调用纪律与费用

- 每次真实检索前确认图片和最终筛选条件，使用最小必要参数；不要用连续请求试探图片、地区、分类、法律状态或 `topK`。
- 当前 MCP skill 不保留旧脚本的缓存、落盘或 stdout 摘要行为。相同 `toolName + arguments` 在一个任务内去重；若用户要求不同请求，先提示可能产生额外积分消耗。
- MCP 返回的成功结果可展示实际费用字段。来源 `data.usage`、后端成本、空费用字段和候选数量都不能用来推算用户扣费。
- 失败、空结果、覆盖不足或结果不明确时停止。不要自动重试、重放、换图、改参数、跟随重定向或轮询。

## 错误处理

| 情况 | 处理 |
|---|---|
| MCP 连接、schema 或 `isError` 错误 | 停止业务调用，报告 MCP 错误并读取 `onboarding.md` |
| 400 或参数错误 | 展示具体字段错误，等待用户修正，不自动改变请求 |
| 下游 401 或认证错误 | 按 onboarding 处理 WorkBuddy 自动授权，不要求用户补传凭证 |
| 下游 402、积分或余额不足 | 按 onboarding 引导用户自助处理，不自动购买、支付或轮询 |
| 下游 403 | 按实际权限错误处理，不归类为余额问题，不自动重试 |
| 上游 code 不是 `OK` 或 envelope 含 error | 保留实际 code、message 和请求标识，不当作候选成功 |
| 5xx、超时或连接中断 | 说明执行结果可能未知，不自动重试；已有请求标识按实际返回保留 |
| coverage 无法建立或出现覆盖警告 | 保留警告和限制，不能解释成零命中或无侵权 |

## 反馈契约

当用户明确表达结果不符合预期、结果错误、满意、不满或提出具体改进时，若当前环境允许反馈，使用脱敏摘要提交反馈。反馈对象包含：

```json
{
  "skillName": "linkfox-wb-sif-compliance-detection",
  "sentiment": "NEUTRAL",
  "category": "BUG",
  "content": "脱敏后的预期与实际差异"
}
```

`sentiment` 使用 `POSITIVE`、`NEUTRAL` 或 `NEGATIVE`；`category` 使用 `BUG`、`COMPLAINT`、`SUGGESTION` 或 `OTHER`。不得包含凭证、图片、Base64、原始候选行、完整地址或其他敏感数据。反馈不是本业务检索，不得用反馈通道替代 `LinkFox.proxy_call`。
