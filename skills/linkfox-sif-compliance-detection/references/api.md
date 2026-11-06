# SIF 外观专利检测 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

| 动作 | POST 路径 | 入口脚本 | 每次新调用 |
|---|---|---|---|
| 图片相似检索 | `/ecDw/designSimilarSearch` | `ec_dw_design_similar_search.py` | 0 算力（￥0） |
| 登记详情 | `/ecDw/designProfile` | `ec_dw_design_profile.py` | 0 算力（￥0） |

两个入口均通过公共 `call_api.run` 发送一次请求；分别映射上游 `search_similar_design`、`get_design_profile`，客户端不接触上游签名或凭据。公开登记仅列相似检索，登记详情保留为按需调用的兼容能力。

## 接口：外观相似检索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ecDw/designSimilarSearch`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `imageUrl` | string | 图片来源二选一 | — | 公网 HTTP(S) 地址，8–4096 字符，无内嵌 URL 凭据 |
| `imageBase64` | string | 图片来源二选一 | — | 图片字节的纯 Base64，不含 `data:image/...;base64,` 前缀；16–20971520 字符，上限为 20 MiB Base64 文本，约对应 15 MiB 原图 |
| `title` | string | 否 | — | 如提供则 1–4096 字符；只能辅助图片，不能代替图片 |
| `topK` | integer | 否 | 20 | 1–200；候选上限不是用户计费单位，不能据此推算用户售价 |
| `regions` | string[] | 否 | — | ISO-2 地区码，如 CN/US/EM；每项 2 个英文字母，最多 64 项，不重复。欧盟来源码 EU 在本参数用 EM |
| `jurisdictionCodes` | string[] | 否 | — | 来源归属码，如 USID/EMID；每项 2–8 个英文字母，最多 32 项，不重复。不是 ISO-2 码；同时给 regions 时取交集 |
| `topLoc` | string[] | 否 | — | 洛迦诺主分类前缀，每项 2 位数字，如 `["09","22"]`；最多 32 项，不重复，不传字符串或数字标量 |
| `locarnoClasses` | string[] | 否 | — | 洛迦诺分类，每项格式 NN-NN，如 22-06；最多 64 项，不重复 |
| `patentStatus` | integer[] | 否 | — | 当前网关统一使用数组：`[0]` 仅失效、`[1]` 仅有效、`[0,1]` 两者；1–2 项且不重复，仅允许整数 0/1，不传整数标量。省略时不预设法律状态偏好 |

`imageUrl` 与 `imageBase64` 必须且只能提供一个；只有 title 或同时提供两种图片来源均无效。字段使用 camelCase，由后端映射成上游 `image_url` / `image_base64` / `top_k` / `jurisdiction_codes` / `top_loc` / `locarno_classes` / `patent_status`；title 和 regions 同名透传。patentStatus 保持数组，不使用上游的标量写法。

文本字段不能含首尾空白；筛选数组不能含 null 或重复项。可选参数没有使用时优先省略，不用空字符串、数字字符串或逗号拼接字符串代替正确类型。除 patentStatus 外，其他筛选数组允许空数组；省略比空数组更明确。脚本只检查 JSON 顶层为对象；后端校验字段组合、长度、范围、筛选格式和 Base64 文本合法性。图片解码及 URL 下载由上游执行，不能把通过网关初步校验当成有效图片验证。`topK` 必须为 JSON 整数，不传小数、布尔值或数字字符串。

来源归属码与 ISO-2 地区码不能混用；不要把候选的 `registration_jurisdiction_code` 或登记号中的来源标识机械改写成 regions。缺分类或法律状态未知的候选按实际返回展示；不承诺显式 `[0,1]` 一定留下或剔除 unknown，也不自行重筛候选。

本地图可直接编码为 `imageBase64`，无需上传 helper；脚本不转换图片格式。20 MiB 是单个 Base64 字段的上限；JSON 封装后的整个请求字节数、网关/Ingress/来源服务限制是独立层级。脚本不自动压缩、转图或改参数；遇到 413 时保留请求号，核对对应层级限制。

仅使用上述九个业务字段，不加入 query_mode、上游 URL、凭据或自定义请求头。签名、AccessKey/SecretKey 和 nonce 由后端托管；后端映射上游工具 search_similar_design。

#### 国家与区域覆盖

按 SIF 提供的数据来源口径，当前覆盖 42 个国家。H 表示海牙登记归属，L 表示本土或区域局来源，H+L 表示两套来源都有。括号内的两字母地区码用于 `regions`，H 和 L 用于说明数据来源。保护法域以结果中的 `protected_jurisdictions` 为准。

- **亚洲（17）**：中国（CN，H）、日本（JP，H）、韩国（KR，H）、印度（IN，H）、印度尼西亚（ID，H）、泰国（TH，H）、越南（VN，H）、马来西亚（MY，H）、新加坡（SG，H）、菲律宾（PH，H）、斯里兰卡（LK，H）、柬埔寨（KH，H）、老挝（LA，H）、蒙古（MN，H）、约旦（JO，H）、以色列（IL，H）、文莱（BN，H）
- **欧洲（14）**：英国（GB，L）、德国（DE，H）、法国（FR，H）、西班牙（ES，H）、意大利（IT，H）、瑞士（CH，H）、挪威（NO，H）、保加利亚（BG，H）、克罗地亚（HR，H）、摩尔多瓦（MD，H）、北马其顿（MK，H）、阿尔巴尼亚（AL，H）、乌克兰（UA，H）、格鲁吉亚（GE，H）
- **美洲（4）**：美国（US，H+L）、加拿大（CA，H+L）、秘鲁（PE，H）、哥斯达黎加（CR，H）
- **大洋洲（2）**：新西兰（NZ，H）、澳大利亚（AU，L）
- **非洲（5）**：突尼斯（TN，H）、肯尼亚（KE，H）、埃及（EG，H）、博茨瓦纳（BW，H）、莫桑比克（MZ，H）

欧盟的区域标签单列，不计入 42 个国家。

- **EU**：欧盟，EUIPO 本地来源。
- **EM**：海牙欧盟区域。按欧盟筛选时，`regions` 使用 `EM`。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| JSON 位置参数 | JSON object | 与 --params-file 二选一 | — | 与文件入参等价；仅检查顶层为对象，业务字段校验由后端处理。 |
| --params-file | CLI path | 与 JSON 位置参数二选一 | — | UTF-8 JSON 文件，接受 BOM；大 Base64 图片优先使用文件，避免 Windows 命令行长度限制。 |
| --inline | CLI flag | 否 | 关闭 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过业务脚本缓存的读写，主动刷新会发送一次新请求，不启用重试。 |

- Python 3.9+，两个业务入口仅依赖标准库。LINKFOX_TOOL_GATEWAY 优先覆盖默认网关，密钥优先 LINKFOX_AGENT_API_KEY、回退 LINKFOXAGENT_API_KEY。
- 透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME；HTTP 头建议 ASCII，不含控制字符，不能按 Latin-1 编码时在请求前返回清晰错误，只提示头名，不回显密钥。JSON 参数正常支持 UTF-8 中文。
- 每次至多一个请求，不自动重试、不跟随重定向，不自动更换图片或条件。入口调用公共 call_api.run；响应兼容、缓存和输出策略由业务包装维护，公共调用器缓存始终禁用，其输出重定向至内存，避免重复缓存或结果副本。
- 成功响应仅由业务脚本缓存管理：按网关、端点、API Key 指纹及完整参数隔离 24 小时；HTTP/业务失败不缓存。缓存读取前仍需配置当前 Key，但命中不联网验证 Key 是否仍有效；不保存原始 Key 或额外请求正文。图片检索另按 v3 响应契约隔离，不读取旧版检索缓存。
- 请求前准备最终 session/data 并独占预留唯一文件。SESSION_ID 控制字符、路径字符、Windows 保留名、尾部点或空白均在请求前拒绝。当前工作目录不可写即报错，不回退家目录或临时目录。输出路径与大小策略见 [SKILL.md](../SKILL.md#输出策略)。

### 响应结构

外层 `data` 是上游完整 envelope，`data.data` 才是业务对象。后端使用动态 Map 原样透传字段和数组顺序；公共 HTTP 序列化可能省略对象中值为 null 的字段，缺省与 null 均展示为“来源未提供”。成功需同时满足 HTTP 2xx、网关状态符合公共响应规则、上游 `data.code=OK` 且无业务失败标记，不能只看 HTTP 200 或进程退出码。不因缺少已删除诊断字段而判失败。

| 路径 | 类型 | 说明 |
|---|---|---|
| `errcode`, `errmsg` | integer, string | 网关状态与消息；成功响应示例为 200，按公共规则判断，错误保留实际代码和消息 |
| `data` | object | 上游 envelope；错误时可能不存在 |
| `data.code`, `data.message` | string | 上游业务状态与消息；成功为 OK / success |
| `data.request_id`, `upstreamRequestId` | string | 上游请求标识；后者由后端提取 |
| `requestId` | string | 网关/服务错误请求标识，与上游 request_id 分开；XML 归一化也保留 |
| `data.data` | object | 检索业务对象 |
| `data.data.candidates` | object[] | 候选数组，按返回顺序展示；空数组不代表无侵权风险 |
| `data.data.total` | integer | 本次返回的候选数量，不是全库数量或用户计费单位 |
| `data.usage` | object | 来源账户用量；credit_cost 为来源积分，credit_waived 为来源费用豁免标记，不是用户扣费或余额 |
| `costToken`, `costCredit` | integer | 脚本合入网关 X-Cost-Token / X-Cost-Credit，响应头优先；检索与详情定价均为 0 / 0，实际以返回为准；缺省不代表免费 |
| `httpStatus`, `error`, `details` | integer, string, string | 脚本归一化失败时的 HTTP 状态、错误及非 JSON 正文；费用字段不证明成功 |

#### 候选字段（v3.0）

公开契约共 29 个业务字段，以下均相对于 `data.data.candidates[]`。日期为 YYYY-MM-DD；字段可缺省或为 null，均不补造事实。免费工具目录未提供 outputSchema；仅给出 null/空数组样例的非空结构不作额外假设，按实际 JSON 原值处理。

| 字段 | 类型 | 展示语义 |
|---|---|---|
| `design_registration_id` | string | 原样用于登记详情查询的唯一标识 |
| `registration_jurisdiction_code` | string | 来源归属码，如 EU、EMID、USID；不机械改写成 ISO-2 |
| `jurisdiction_iso2` | string | 来源登记归属，如 EM、US、WO，与保护法域分开 |
| `primary_identifier` | string | 主展示号码，保留前导零 |
| `application_number` | string | 申请号 |
| `registration_number` | string | 登记号 |
| `publication_number` | string | 公布号 |
| `title` | string | 来源标题，可能为号码 |
| `title_language` | string | 来源标题语言，可能为 unknown |
| `title_en` | string | 来源英文标题，不自行补译 |
| `designer_names` | string[] | 设计人信息 |
| `locarno_classes` | string[] | 原样保留分类，如 06.01 或 09-01；输出格式不改变请求 NN-NN 约束 |
| `holder_names` | string[] | 来源权利人信息；数字标识不自行还原为名称 |
| `simple_legal_status` | string | 来源法律状态，不根据相似度重新推断 |
| `application_date` | string | 申请日期 |
| `registration_date` | string | 登记日期 |
| `publication_date` | string | 公布日期 |
| `similarity` | number | 最终 0–100 排序分，数组中非递增；不是概率或侵权概率，不计算、不乘100、不重排 |
| `risk_level` | string | 来源风险提示，与分数和法律状态分别保留，不推断固定阈值或侵权结论 |
| `image_url` | string | 首图完整公网签名地址；有图时等于 images[0] |
| `images` | string[] | 最多6张完整签名图，按原顺序；空数组表示无可用图片 |
| `specification` | JSON/null | 来源说明书/说明内容；非空结构按实际返回，不补写 |
| `novelty_statement` | string/null | 来源新颖性声明；例如 No，保留原文，不转成法律判断 |
| `applicant_addresses` | object[]/null | 来源申请人地址；本次实测元素含 name、address 字符串，不补造归属 |
| `locarno_details` | object[] | 分类代码及文案，下表说明子字段 |
| `estimated_expiration_date` | string/null | 预估到期日，必须标注为估算，不能当成已确认失效 |
| `expiration_date_basis` | JSON/null | 预估依据，按原值展示，缺失时不自拟计算依据 |
| `tro_cases` | array | 当前 TRO 语料关联记录，元素结构按实际返回；空数组不是“确认无TRO” |
| `protected_jurisdictions` | string[]/null | HAGUE 为指定保护国，普通登记为归属法域；null 为未知，不能由 regions 补齐 |

| `locarno_details[]` 子字段 | 类型 | 说明 |
|---|---|---|
| `code` | string | 分类原始代码，如 06.01 |
| `parent_code` | string | 主分类代码，如 06 |
| `label_zh`, `label_en` | string/null | 来源中英文文案；当前部分 EUIPO 点号格式可能未命中文案，null 按“来源未提供”展示，不自行猜名称 |

| `applicant_addresses[]` 子字段（本次实测） | 类型 | 说明 |
|---|---|---|
| `name` | string | 来源申请人名称，缺省不从其他候选补齐 |
| `address` | string | 来源地址原文，不据此推断保护法域 |

按候选数组顺序展示 Top-K，包括同分项；不自行按相似度、状态或 TRO 重排。`similarity` 已反映最终顺序，不沿用旧版原始图文分数口径。上游 v3 不再返回 `image_score`、`text_score`、`matched_modality`、`image_available`、`title_en_source`、`risk_reasons` 以及模型、索引、coverage、warnings、耗时等内部诊断，不再把这些作为结果展示或成功判断的必要字段。

图片使用返回原始完整 URL，不替换域名或删改签名；`image_url` 是 `images` 的首张，不重复算一张。签名有效期7天，不存数据库或当永久地址；会话原始 JSON 仅是查询时的历史记录，24h 查询缓存也不会延长图片有效期。优先显示首图，按需展示或懒加载其他视图，不批量下载所有图片，不自动重新检索以刷新过期地址。通常默认 topK=20 即可，50个候选约125KB只是来源示例，不作固定大小保证。

保护法域按 `protected_jurisdictions` 展示，不把登记归属、请求地区和实际保护范围混为一谈。`tro_cases=[]` 只表示当前语料未关联，不能解释为无诉讼或零风险。未提供的数据集覆盖信息不推算、不补造；空结果或上游失败均不能解释为不存在相关专利。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游 `data.code` 必须为 `OK`；响应携带 `httpStatus` 时也须为 200–299。错误响应、非 null 的 error（含空字符串/空对象）、success=false 或 ok=false 等实际错误标记不作为成功结果，且不缓存；读取旧缓存时也跳过失败响应。费用字段存在不表示业务成功。失败或空列表均不自动重试。

| 情况 | 处理 |
|---|---|
| 400 / 无效参数 | 展示实际字段错误；不自动改变图片、筛选或候选数 |
| 400 / DATA_IMAGE_DOWNLOAD_FAILED | 来源下载图片失败；保留错误和请求号，核对实际 URL 与来源日志，不擅自断言参数错误、不自动换图或改用 Base64 重试 |
| 413 / SYSTEM_PAYLOAD_TOO_LARGE | 核对字段与整包限制，保留错误和请求号；不自动压缩、换图或重试 |
| 404 / DATA_DESIGN_NOT_FOUND | 来源未找到详情，不自动换号码或查询方式；普通 not found 另核对网关路由/服务版本 |
| 上游认证错误（如 AUTH_ACCESS_KEY_INVALID）/ 数仓服务凭据未配置 | 联系后端管理员检查上游配置，保留 code/request_id；客户端不索取上游 AccessKey/SecretKey 或门户口令 |
| 403 | 按实际权限错误处理，不绕过授权或索取上游凭据 |
| 3xx | 返回 Redirect blocked，不转发 Key、不跟随重定向 |
| Invalid request header | 环境变量头含控制字符或不能按 Latin-1 编码；只提示头名称，不回显 Key，不发请求。将透传头改成 ASCII 标识后由用户决定后续调用 |
| 5xx / 超时 / 连接中断 | 不自动重试；调用结果可能未知，保留已有请求标识 |
| 502 / SR_QUERY_ERROR、503 / CAPABILITY_BACKEND_UNAVAILABLE | 来源查询失败或能力后端不可用；保留实际 code/request_id，不作为零命中或引导用户充值的依据 |
| LinkFox 网关 401 / 402 / 算力或余额不足 | 读取 [onboarding.md](onboarding.md)，处理用户 Key、认证和算力问题 |
| 覆盖度不足或无法建立 | 保留来源失败/警告；不能当作零命中或无侵权结论 |

XML `ToolErrorResponse` 也保留实际 `requestId` 及其他返回字段，不只保留 errcode/errmsg。

### 费用与缓存解释

检索与详情当前均为 0 算力/次（￥0/次）。详情单次支持 1–200 个 ID，不按返回条数收费。缓存命中不发请求，缓存费用仍为原始响应值。实际费用以网关返回为准，候选数、后端成本、来源积分及空费用字段均不能推算用户扣费或免费。若返回非零费用，原样展示并提示管理员核对网关配置，不自动重新调用。

### 响应示例

以下示例仅展示 v3 响应结构。图片地址为占位符，费用按 0 算力定价填写，实际以网关返回为准。

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
      "candidates": [{
        "design_registration_id": "DSR:euipo_design:001694860-0001",
        "registration_jurisdiction_code": "EU",
        "jurisdiction_iso2": "EM",
        "primary_identifier": "001694860-0001",
        "application_number": "001694860",
        "registration_number": "E077151-PC",
        "publication_number": null,
        "title": "E077151-PC",
        "title_language": "unknown",
        "title_en": "Chairs [seats]",
        "designer_names": null,
        "locarno_classes": ["06.01"],
        "holder_names": ["237302"],
        "simple_legal_status": "inactive",
        "application_date": "2010-04-13",
        "registration_date": null,
        "publication_date": null,
        "similarity": 99.88,
        "risk_level": "medium",
        "image_url": "<第1张完整签名URL>",
        "images": ["<第1张完整签名URL>", "<第2张完整签名URL>"],
        "specification": null,
        "novelty_statement": null,
        "applicant_addresses": null,
        "locarno_details": [{"code": "06.01", "parent_code": "06", "label_zh": null, "label_en": null}],
        "estimated_expiration_date": null,
        "expiration_date_basis": null,
        "tro_cases": [],
        "protected_jurisdictions": ["EM"]
      }],
      "total": 1
    },
    "usage": {"credit_cost": 35, "credit_waived": false}
  },
  "costToken": 0,
  "costCredit": 0
}
```

### curl 示例

```bash
curl --request POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/ecDw/designSimilarSearch" \
  --header "Authorization: ${LINKFOX_AGENT_API_KEY:-${LINKFOXAGENT_API_KEY}}" \
  --header 'Content-Type: application/json' \
  --header 'User-Agent: LinkFox-Skill/2.0' \
  --header "SESSION_ID: ${SESSION_ID}" \
  --header "MESSAGE_ID: ${MESSAGE_ID}" \
  --header "MODE_ID: ${MODE_ID}" \
  --header "APP_NAME: ${APP_NAME}" \
  --data-binary @request.json
```

这是 Bash 的协议示例，`request.json` 按 [SKILL.md](../SKILL.md#使用示例) 示例从真实本地图生成，不使用占位图片地址。curl 本身不提供缓存、自动落盘和费用头合并；正式工作流优先直接入口脚本：`python scripts/ec_dw_design_similar_search.py --params-file request.json [--inline]`。不要再用 curl 重复已由脚本完成的请求。

## 接口：外观登记详情

`POST /ecDw/designProfile`。使用检索返回或用户提供的外观登记标识查询详情，无需先发起新的图片检索；不提供独立的通用专利公开号查询或专利全文检索。

### 调用规范

- 基本规则参考 `公共规则`；与图片检索共用脚本选项、缓存及输出约定，缓存按端点隔离。
- 每次仅发起一个详情请求，不隐式先检索或分批循环。

### 请求参数

| 参数 | 类型 | 约束 | 上游字段 |
|---|---|---|---|
| `designRegistrationIds` | string[] | 与 primaryIdentifier 严格二选一；1–200 个唯一登记 ID，每项 1–128 字符，无 null、空字符串或首尾空白 | `design_registration_ids` |
| `primaryIdentifier` | string | 与 designRegistrationIds 严格二选一；1–128 字符，无首尾空白；主号码可能重号 | `primary_identifier` |
| `jurisdictionIso2` | string | 可选，仅用于 primaryIdentifier 方式；两位英文字母，如 US/EM，用于收敛归属 | `jurisdiction_iso2` |

所有号码均传字符串，保留前导零；不接受数字/布尔值替代字符串。优先原样使用候选的 `design_registration_id`，不要把 `registration_number` 或 `publication_number` 拼成登记 ID。一次最多 200 个，不自动拆分或逐条请求；不向详情传图片或检索筛选参数。

```bash
python scripts/ec_dw_design_profile.py '{"designRegistrationIds":["DSR:wipo_hague:EMID.001431738-0001"]}'
```

也支持 `--params-file detail-request.json`；主号码方式的 JSON 为 `{"primaryIdentifier":"001431738","jurisdictionIso2":"EM"}`。示例使用已验证标识，实际业务应替换为用户提供或检索返回的标识，不为演示重复查询。

### 响应结构

成功需满足本页公共 HTTP/errcode 规则、上游 `data.code=OK`，且没有实际错误标记。以下按已验证生产响应的业务结构删减，费用示例按 0 算力定价填写，每次仍以实际费用头为准；字段值只表示该登记的来源记录：

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "upstreamRequestId": "req_example",
  "data": {
    "code": "OK",
    "message": "success",
    "request_id": "req_example",
    "data": {
      "asset": "asset.design_profile",
      "asset_code": "asset_ipr_design_profile",
      "returned": 1,
      "items": [{
        "design_registration_id": "DSR:wipo_hague:EMID.001431738-0001",
        "primary_identifier": "001431738",
        "title_en": "Bottles",
        "simple_legal_status": "inactive",
        "as_of_date": "2026-10-09",
        "coverage_level": "detail_ready",
        "has_readable_image": 1,
        "image_count": 5
      }],
      "execution": {"engine": "starrocks", "elapsed_ms": 27, "row_count": 1}
    }
  },
  "costToken": 0,
  "costCredit": 0
}
```

| 路径 | 类型 | 说明 |
|---|---|---|
| `data.data.items` | object[] | 登记详情列表，不能套用检索 candidates 路径；保留全部返回记录和原顺序 |
| `data.data.returned` | integer | 本次返回记录数，不代表来源资产总量 |
| `data.data.asset`, `data.data.asset_code` | string | 来源资产标识 |
| `data.data.execution` | object | 来源执行元数据，实测含 engine（string）、elapsed_ms / row_count（integer）；非用户主结果 |
| `data.usage` | object | 原始来源用量，沿用上文语义；不是用户扣费或余额 |
| `upstreamRequestId`, `data.request_id`, `costToken`, `costCredit` | string / integer | 请求追踪和网关费用，沿用公共 envelope 规则；费用头优先 |

下表列出上游字典的 30 个字段，路径均为 `data.data.items[]`。生产记录可能只返回其中部分字段；缺省/null 表示来源未知，不补值，不承诺每条记录完整返回字典字段。

| 字段 | 类型 | 语义 |
|---|---|---|
| `design_registration_id` | string | 来源外观登记唯一 ID |
| `primary_identifier` | string | 主展示号码，保留前导零 |
| `application_number` | string | 申请号 |
| `registration_number` | string | 登记号或国际登记号 |
| `publication_number` | string | 公开号 |
| `as_of_date` | string | 最近一次确认/重算的业务日期，不表示今天或历史快照 |
| `data_version` | string | 来源数据版本 |
| `right_type` | string | 权利类型，实测为 registered_design |
| `registration_jurisdiction` | string | 来源归属原值，实测为 EM，不保证为中文国家名 |
| `registration_jurisdiction_code` | string | 原始归属码，如 EMID/USID |
| `jurisdiction_iso2` | string | ISO-2 归属，欧盟使用 EM |
| `title` | string | 来源原始标题 |
| `title_language` | string | 标题语言，可能为 unknown |
| `title_en` | string | 来源英文标题，不自行补译 |
| `title_en_source` | string | 英文标题来源 |
| `simple_legal_status` | string | 归一状态，如 active/inactive/pending/unknown，保留来源口径 |
| `raw_status` | string | 来源状态原文，实测为 DEL，不自行重新映射 |
| `application_date` | string | 申请日期，YYYY-MM-DD |
| `registration_date` | string | 登记日期，YYYY-MM-DD |
| `publication_date` | string | 公开日期，YYYY-MM-DD |
| `locarno_classes` | string[] | 来源洛迦诺分类 |
| `holder_names` | string[] | 权利人名称 |
| `designer_names` | string[] | 设计人名称 |
| `classification_count` | integer | 分类事实条数 |
| `party_count` | integer | 主体事实条数，不推断缺失的持有人或设计人 |
| `has_readable_image` | integer | 生产实测为 1；按原类型保留，表示媒体可读提示，不是图片 URL |
| `image_count` | integer | 来源图片事实数量，不代表可下载文件数量 |
| `text_count` | integer | 来源文本事实数量 |
| `data_quality_level` | string | 来源数据质量等级，如 usable/partial/insufficient |
| `coverage_level` | string | 来源覆盖等级，如 detail_ready/search_ready/metadata_partial/identifier_only/insufficient_data |

详情不返回图片地址、封面、对象存储定位或侵权结论；不能由 `has_readable_image` / `image_count` 构造下载链接。详情没有检索生成的模态分数或相似度。主号码返回多条时保留全部，不擅自认定首条为唯一结果。`404 / DATA_DESIGN_NOT_FOUND` 只表示来源未找到对应登记，不能推断不存在相关权利。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sif-compliance-detection",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
