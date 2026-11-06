# linkfox-sif-compliance-detection 业务参考

本参考归档当前 WorkBuddy 可用的 SIF 外观相似检索业务。它只对应 `ecDw/designSimilarSearch`，由 `LinkFox.proxy_call` 调用；完整字段约束和响应字典见同目录 [api.md](api.md)。

## 功能与边界

- 输入一张商品图片，返回外观登记相似候选，支持标题辅助、地区、来源归属、洛迦诺分类和法律状态筛选。
- 返回结果用于候选排查与人工复核，不能用于直接下侵权、无侵权、自由实施或安全结论。
- 当前路由不提供按登记 ID、主号码或公开号获取详情的 operation，也不提供专利全文、独立商标检索或独立 TRO 检索。
- 本地图片可以直接编码为 `imageBase64`，不需要上传流程；`imageUrl` 与 `imageBase64` 严格二选一。
- 相同参数在同一任务中只调用一次。失败、空结果和字段缺失不触发自动改图、重试或放大候选数。

## MCP 路由

| 业务目的 | 原 endpoint | 精确 `toolName` | 业务结果路径 |
|---|---|---|---|
| 商品图片外观相似登记候选检索 | `/ecDw/designSimilarSearch` | `ecDw/designSimilarSearch` | `data.data.candidates[]` |

调用外壳固定为：

```json
{
  "toolName": "ecDw/designSimilarSearch",
  "arguments": {
    "imageUrl": "https://public.example/product.png"
  }
}
```

`arguments` 是原业务请求对象，不包 `body`、`params`、`data` 或第二层 `arguments`。WorkBuddy 自动注入授权，禁止传 headers 或任何凭证字段。

## 请求规则

| 参数 | 类型 | 必填 | 约束与用途 |
|---|---|---:|---|
| `imageUrl` | string | 与 `imageBase64` 二选一 | 公网 HTTP(S) 纯 URL，建议 8–4096 字符；不要传 Markdown、HTML 或带凭证的 URL |
| `imageBase64` | string | 与 `imageUrl` 二选一 | 图片字节的纯 Base64，不含 data URL 前缀；16–12,582,912 个字符，按当前 MCP schema 校验 |
| `title` | string | 否 | 图片上下文，1–4096 字符；只能辅助图片，不能替代图片 |
| `topK` | integer | 否 | 默认 20，范围 1–200；只能传 JSON 整数 |
| `regions` | string[] | 否 | 最多 64 个不重复 ISO-2 地区码，例如 `CN`、`US`、`EM`；欧盟在该字段使用 `EM` |
| `jurisdictionCodes` | string[] | 否 | 最多 32 个不重复来源归属码，例如 `USID`、`EMID`；不是 ISO-2 地区码 |
| `topLoc` | string[] | 否 | 最多 32 个不重复的两位数字洛迦诺主分类前缀，例如 `09`、`22` |
| `locarnoClasses` | string[] | 否 | 最多 64 个不重复分类码，例如 `22-06` |
| `patentStatus` | integer[] | 否 | 只允许 `[0]`、`[1]` 或 `[0,1]`；省略时不预设法律状态偏好 |

字段名使用 camelCase。可选字段不使用时优先省略，不用空字符串、数字字符串或逗号拼接字符串代替正确类型。筛选数组不可含 null 或重复项；来源未分类或状态 unknown/pending 的候选由上游决定，客户端不自行删除。

`regions` 与 `jurisdictionCodes` 同时提供时取交集。`topLoc` 是主分类前缀，`locarnoClasses` 是完整分类，两者不能互相改写。`patentStatus` 必须是数组，不能传整数标量。

## 响应与成功判断

先处理 MCP 外层状态，再处理业务 JSON。text content 若为 JSON 只解析一次。业务成功同时要求下游 `errcode=200`、`data.code=OK` 且没有明确的业务失败标记；不能只因 MCP 调用返回或外层传输成功就展示候选。

成功业务对象通常位于 `data.data`：

- `data.data.candidates` 是候选数组，保留原顺序。
- `data.data.total` 是本次返回数量，不是全库数量，也不是计费单位。
- `data.request_id` 与 `upstreamRequestId` 是请求追踪标识。
- `costCredit` 和 `costToken` 是本次调用费用信息，缺省不等于免费；`data.usage.credit_cost` 是来源侧用量，不作为用户价格。

来源字段可以缺省或为 null，显示为“来源未提供”，不补造事实。以下字段应按原值保留：

| 字段 | 展示与后续复核用途 |
|---|---|
| `design_registration_id` | 来源登记唯一标识；当前能力只展示，不拼接为未暴露的详情请求 |
| `registration_jurisdiction_code` | 来源归属码，例如 EU、EMID 或 USID，不改写成地区码 |
| `jurisdiction_iso2` | 来源 ISO-2 归属，例如 EM、US、WO |
| `primary_identifier`、`application_number`、`registration_number`、`publication_number` | 原始登记标识，保留前导零 |
| `title`、`title_en`、`title_language` | 来源标题和语言，不自行翻译 |
| `designer_names`、`holder_names`、`applicant_addresses` | 来源主体与地址事实，不从数字标识推断名称 |
| `locarno_classes`、`locarno_details` | 来源分类；文案缺失时标为“来源未提供” |
| `simple_legal_status`、`application_date`、`registration_date`、`publication_date` | 来源状态与日期，不根据相似度重新推断 |
| `similarity` | 0–100 最终排序分，不是概率，不重排 |
| `risk_level` | 来源风险提示，与相似度和法律状态分开呈现 |
| `image_url`、`images` | 首图和最多六张签名图，原样使用，不改写 URL |
| `specification`、`novelty_statement` | 来源描述文本，缺失不补写法律含义 |
| `estimated_expiration_date`、`expiration_date_basis` | 估算到期信息，必须标记为估算 |
| `tro_cases` | 当前 TRO 语料关联线索；空数组不等于无 TRO |
| `protected_jurisdictions` | 实际返回的保护法域；不能由请求地区补齐 |

检索 v3 只依赖公开业务字段。不要要求或重构旧版模型、原始分、coverage、warnings、耗时等诊断字段；它们缺失不构成失败。

## 使用和展示特殊规则

1. 先按返回顺序展示候选，再根据用户指定的数量截取展示，不自行重新排序或删除同分项。
2. 图片优先展示 `image_url`，它与 `images[0]` 对应时不要重复计数；签名 URL 有效期有限，不存为永久地址，不批量下载全部视图。
3. `tro_cases=[]` 只能写成“当前来源未关联 TRO 记录”，不能写成“无 TRO”或“安全”。
4. `protected_jurisdictions`、`jurisdiction_iso2`、`registration_jurisdiction_code` 和请求筛选地区分别标注，避免把登记归属误作保护范围。
5. 空结果、来源覆盖不足、404 或业务错误只能表示本次查询未获得候选，不能解释为不存在相关外观权利。
6. 发生需要重新调用的请求时，先提示可能产生新积分消耗，由用户决定是否继续；不自动刷新图片链接。

## 费用与失败纪律

当前目录口径为每次新的检索调用消耗 5 算力，实际以本次返回费用字段为准。相同 `toolName + arguments` 在同一任务中不得重复调用。MCP 缺失、schema 失败、下游 401、402、403、5xx、超时或业务失败时停止，不自动重放、不自动改变输入。

详细的错误状态、反馈字段和参数边界见 [api.md](api.md)；认证与积分分层见 [onboarding.md](onboarding.md)。
