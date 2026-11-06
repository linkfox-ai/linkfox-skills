# SIF 外观相似检索 API 参考

## MCP 调用规范

- MCP server 为 `LinkFox`，唯一业务工具为 `proxy_call`。
- `toolName` 必须是 `ecDw/designSimilarSearch`，保留原路径大小写，不加前导 `/`。
- 原请求对象直接放在 `arguments`。不要增加 `body`、`params`、`data` 或第二层 `arguments`。
- WorkBuddy 自动注入授权。请求中不要包含 headers、Authorization、凭证、token、JWT、手机号或其他认证字段。
- 先处理 MCP 连接、schema 和 `isError`，再解析 structured/text content。text JSON 只解析一次，之后检查业务状态字段。

示例：

```json
{
  "toolName": "ecDw/designSimilarSearch",
  "arguments": {
    "imageUrl": "https://public.example/product.png",
    "topK": 20
  }
}
```

## 请求参数

业务请求对象的字段如下。

| 参数 | 类型 | 必填 | 默认值 | 约束与说明 |
|---|---|---:|---:|---|
| `imageUrl` | string | 与 `imageBase64` 二选一 | — | 公网 HTTP(S) 纯 URL，建议 8–4096 字符；不能是 Markdown、HTML 或含内嵌凭证的 URL |
| `imageBase64` | string | 与 `imageUrl` 二选一 | — | 图片字节的纯 Base64，不含 `data:image/...;base64,` 前缀；16–12,582,912 字符，按当前 MCP schema 校验 |
| `title` | string | 否 | — | 1–4096 字符的辅助上下文，不能替代图片 |
| `topK` | integer | 否 | 20 | 1–200；只能传整数，不传小数、布尔值或数字字符串 |
| `regions` | string[] | 否 | — | 最多 64 个不重复 ISO-2 地区码，例如 `CN`、`US`、`EM`；欧盟使用 `EM` |
| `jurisdictionCodes` | string[] | 否 | — | 最多 32 个不重复来源归属码，例如 `USID`、`EMID`；不是 ISO-2 地区码 |
| `topLoc` | string[] | 否 | — | 最多 32 个不重复两位数字前缀，例如 `09`、`22`；不能传数字标量 |
| `locarnoClasses` | string[] | 否 | — | 最多 64 个不重复完整分类码，例如 `22-06` |
| `patentStatus` | integer[] | 否 | — | 只允许 `[0]`、`[1]` 或 `[0,1]`；不使用整数标量 |

### 组合校验

- `imageUrl` 与 `imageBase64` 必须且只能提供一个。只传 `title`、同时传两种图片来源或两者都不传都无效。
- 文本字段不能含首尾空白。筛选数组不能含 null 或重复项；可选参数不用时优先省略，不用空字符串或逗号拼接字符串代替。
- `regions` 是请求地区筛选，`jurisdictionCodes` 是来源归属筛选；两者同时传入时取交集，不可互换。
- `topLoc` 是两位洛迦诺主分类前缀，`locarnoClasses` 是完整分类码；缺分类由来源决定，不在客户端删除。
- `patentStatus` `[0]` 表示仅失效、`[1]` 表示仅有效、`[0,1]` 表示两者；unknown/pending 由上游规则处理，不自行重筛。
- 本地图片可直接编码为 `imageBase64`，不需要上传 URL。Base64 字段上限是文本字符上限，完整 JSON 包装和服务端整包限制仍可能独立触发。

## 成功响应

成功需同时满足 MCP 调用可用、外层未报 `isError`、下游 `errcode=200`、`data.code=OK` 且没有明确业务失败标记。典型结构如下，图片 URL 和请求 ID 仅为格式示例。

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "upstreamRequestId": "req_example",
  "data": {
    "request_id": "req_example",
    "code": "OK",
    "message": "success",
    "data": {
      "candidates": [
        {
          "design_registration_id": "DSR:example:0001",
          "registration_jurisdiction_code": "USID",
          "jurisdiction_iso2": "US",
          "primary_identifier": "0001",
          "application_number": "0001",
          "registration_number": "R-0001",
          "publication_number": null,
          "title": "Example design",
          "title_language": "en",
          "title_en": "Example design",
          "designer_names": null,
          "locarno_classes": ["09-01"],
          "holder_names": null,
          "simple_legal_status": "unknown",
          "application_date": null,
          "registration_date": null,
          "publication_date": null,
          "similarity": 99.88,
          "risk_level": "medium",
          "image_url": "https://public.example/candidate-1.png",
          "images": ["https://public.example/candidate-1.png"],
          "specification": null,
          "novelty_statement": null,
          "applicant_addresses": null,
          "locarno_details": [],
          "estimated_expiration_date": null,
          "expiration_date_basis": null,
          "tro_cases": [],
          "protected_jurisdictions": ["US"]
        }
      ],
      "total": 1
    },
    "usage": {
      "credit_cost": 35,
      "credit_waived": false
    }
  },
  "costToken": 9999,
  "costCredit": 5
}
```

### 公共 envelope

| 路径 | 类型 | 说明 |
|---|---|---|
| `errcode`、`errmsg` | integer、string | LinkFox 下游状态与消息，成功为 `200` |
| `data.code`、`data.message` | string | 来源业务状态，成功为 `OK` 和成功消息 |
| `data.request_id`、`upstreamRequestId` | string | 来源和代理请求追踪标识 |
| `data.data.candidates` | object[] | 候选数组，按来源返回顺序展示 |
| `data.data.total` | integer | 本次返回数量，不是全库数量或计费单位 |
| `data.usage` | object | 来源侧用量，不能解释为用户扣费或余额 |
| `costToken`、`costCredit` | integer | 本次调用费用字段，优先以返回值为准；缺省不代表免费 |

### 候选字段

以下字段路径均相对于 `data.data.candidates[]`。来源可能省略字段或返回 null；缺省和 null 都按“来源未提供”处理。

| 字段 | 类型 | 语义 |
|---|---|---|
| `design_registration_id` | string | 来源登记唯一标识，供人工复核记录 |
| `registration_jurisdiction_code` | string | 来源归属码，例如 EU、EMID、USID，不改写为 ISO-2 |
| `jurisdiction_iso2` | string | 来源登记归属，例如 EM、US、WO |
| `primary_identifier` | string | 主展示号码，保留前导零 |
| `application_number` | string | 申请号 |
| `registration_number` | string | 登记号 |
| `publication_number` | string | 公开号 |
| `title`、`title_en`、`title_language` | string | 来源标题和语言，不自行补译 |
| `designer_names` | string[] | 来源设计人信息 |
| `holder_names` | string[] | 来源权利人信息，不从数字标识还原名称 |
| `locarno_classes` | string[] | 来源分类，原样保留 |
| `locarno_details` | object[] | 分类代码和来源文案 |
| `simple_legal_status` | string | 来源状态，例如 active、inactive、pending、unknown |
| `application_date`、`registration_date`、`publication_date` | string | 来源日期，通常为 YYYY-MM-DD |
| `similarity` | number | 0–100 最终排序分，不是概率，不重算、不重排 |
| `risk_level` | string | 来源风险提示，与相似度和法律状态分开呈现 |
| `image_url` | string | 首张完整签名图片 URL；有图时通常等于 `images[0]` |
| `images` | string[] | 最多六张完整签名图片 URL，保留原顺序 |
| `specification` | JSON 或 null | 来源说明内容，按实际结构展示 |
| `novelty_statement` | string 或 null | 来源新颖性声明，保留原文，不转成法律判断 |
| `applicant_addresses` | object[] 或 null | 来源申请人地址；只在确需复核时最小化展示 |
| `estimated_expiration_date` | string 或 null | 估算到期日，必须标注为估算 |
| `expiration_date_basis` | JSON 或 null | 估算依据，按原值展示 |
| `tro_cases` | array | 当前 TRO 语料关联记录，空数组不是无 TRO 证明 |
| `protected_jurisdictions` | string[] 或 null | 返回的保护法域；不能由请求地区补齐 |

`locarno_details[]` 的常见字段为 `code`、`parent_code`、`label_zh`、`label_en`。文案为 null 时显示“来源未提供”。`applicant_addresses[]` 的常见字段为 `name` 与 `address`，不据此推断保护法域。

## 费用与调用纪律

- 当前目录口径为每次新的图片检索 5 算力，实际扣费以响应中的 `costCredit` 等费用字段为准。
- `data.usage.credit_cost` 是来源侧用量，不是用户 LinkFox 费用；候选数和 `topK` 也不是用户计费单位。
- 同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果、超时和结果不明确时不自动重试或重放。
- 不保证 MCP 提供旧脚本的 24 小时缓存、自动落盘、stdout 摘要或费用头合并；只根据当前 MCP 响应工作。
- 需要扩大 `topK`、改变图片或刷新签名 URL 时，先说明新的调用可能产生费用，由用户决定是否继续。

## 错误处理

| 情况 | 处理 |
|---|---|
| MCP 工具缺失、schema 错误或 `isError=true` | 停止业务调用，读取 [onboarding.md](onboarding.md)，提示安装或重载 LinkFox，不猜测其他工具名 |
| 下游 JSON 401 | 说明自动授权或下游认证失败，保留原错误并停止，不补传凭证 |
| 下游 JSON 402 或余额不足 | 读取 [onboarding.md](onboarding.md)，引导用户自助处理，不自动选套餐、下单或支付 |
| 403 | 按权限错误处理，不绕过权限，不自动重试 |
| 400 或字段校验错误 | 展示实际字段错误，检查图片来源二选一、类型、长度和筛选格式；不自动改参数 |
| `DATA_IMAGE_DOWNLOAD_FAILED` | 说明来源图片下载失败，核对 URL 可访问性；不自动换图或改用另一来源重试 |
| `SYSTEM_PAYLOAD_TOO_LARGE` 或 413 | 说明请求包或 Base64 超限；由用户决定更换较小图片，不自动压缩或重试 |
| 5xx、连接中断或超时 | 说明结果可能未知，不自动重放；保留已有请求标识 |
| `data.code` 不是 `OK` 或响应含业务 `error` | 保留业务 code 和消息，不当作候选结果，不解释成零命中 |
| 空 `candidates` | 如实报告本次没有返回候选，不解释为不存在相关权利或无风险 |

## 展示与反馈

展示时保留候选原顺序、字段原值和来源时间语义。图片签名 URL 只按需展示，不保存为永久地址；`tro_cases`、法律状态和 `risk_level` 都要加来源限定语。

如用户明确反馈结果错误、与意图不符、满意或不满，可按独立反馈契约提交脱敏摘要。反馈不属于业务检索，不得携带图片、Base64、凭证、完整地址、电话号码或原始数据行。

```json
{
  "skillName": "linkfox-wb-sif-compliance-detection",
  "sentiment": "NEUTRAL",
  "category": "BUG",
  "content": "脱敏后的预期与实际差异"
}
```

反馈类别可用 `BUG`、`COMPLAINT`、`SUGGESTION` 或 `OTHER`，情绪可用 `POSITIVE`、`NEUTRAL` 或 `NEGATIVE`。是否发送取决于用户授权和当前环境，不自动重复发送。
