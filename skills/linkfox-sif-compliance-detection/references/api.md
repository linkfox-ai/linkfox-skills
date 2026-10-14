# SIF-外观专利检测 API 参考（外观相似检索）

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ecDw/designSimilarSearch`；网关变量缺省为 `https://tool-gateway.linkfox.com`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：`Authorization: <api_key>`；优先 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；未配置按 SKILL.md 的“解决认证和算力问题”处理
- **User-Agent**：`LinkFox-Skill/2.0`；透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`
- **透传头取值**：建议使用 ASCII，不能含控制字符；标准库使用 Latin-1 编码 HTTP 头。中文等无法编码的值在发送前返回清晰错误，不做隐式编码或重试；JSON 参数仍正常支持 UTF-8 中文
- **超时**：150s；Python 3.9+，仅标准库；每次至多一次请求，不自动重试、不跟随重定向
- **上游映射**：后端调用上游工具 `search_similar_design`；签名、AccessKey/SecretKey、nonce 等由后端托管，客户端不配置上游凭据

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `imageUrl` | string | 图片来源二选一 | — | 公网 HTTP(S) 地址，8–4096 字符，无内嵌 URL 凭据 |
| `imageBase64` | string | 图片来源二选一 | — | 图片字节的纯 Base64，不含 `data:image/...;base64,` 前缀；16–12582912 字符，限制按编码字符串长度计，不是解码文件大小 |
| `title` | string | 否 | — | 如提供则 1–4096 字符；只能辅助图片，不能代替图片。图文分别检索，原始分数不可相加 |
| `topK` | integer | 否 | 20 | 1–200；候选上限不是用户计费单位，不能据此推算用户售价 |
| `regions` | string[] | 否 | — | ISO-2 地区码，如 CN/US/EM；每项 2 个英文字母，最多 64 项，不重复。欧盟来源码 EU 在本参数用 EM |
| `jurisdictionCodes` | string[] | 否 | — | 来源归属码，如 USID/EMID；每项 2–8 个英文字母，最多 32 项，不重复。不是 ISO-2 码；同时给 regions 时取交集 |
| `topLoc` | string[] | 否 | — | 洛迦诺主分类前缀，每项 2 位数字，如 `["09","22"]`；最多 32 项，不重复，不传字符串或数字标量 |
| `locarnoClasses` | string[] | 否 | — | 洛迦诺分类，每项格式 NN-NN，如 22-06；最多 64 项，不重复 |
| `patentStatus` | integer[] | 否 | — | 当前网关统一使用数组：`[0]` 仅失效、`[1]` 仅有效、`[0,1]` 两者；1–2 项且不重复，仅允许整数 0/1，不传整数标量。省略时不预设法律状态偏好 |

`imageUrl` 与 `imageBase64` 必须且只能提供一个；只有 title 或同时提供两种图片来源均无效。字段使用 camelCase，由后端映射成上游 `image_url` / `image_base64` / `top_k` / `jurisdiction_codes` / `top_loc` / `locarno_classes` / `patent_status`；title 和 regions 同名透传。patentStatus 保持数组，不使用上游的标量写法。

文本字段不能含首尾空白；筛选数组不能含 null 或重复项。可选参数没有使用时优先省略，不用空字符串、数字字符串或逗号拼接字符串代替正确类型。除 patentStatus 外，其他筛选数组允许空数组；省略比空数组更明确。脚本只检查 JSON 顶层为对象，业务字段校验由后端执行并返回 400。

来源归属码与 ISO-2 地区码不能混用；不要把候选的 `registration_jurisdiction_code` 或登记号中的来源标识机械改写成 regions。缺分类的登记按上游规则默认保留并计入 `metadata_unknown`，客户端不得自行删掉。法律状态 unknown/pending 的包含关系与覆盖度以实际响应为准；不承诺显式 `[0,1]` 一定留下或剔除 unknown，也不自行重筛候选。

本地图可直接编码为 `imageBase64`，无需上传 helper。大图片先准备本地 UTF-8 JSON 文件，再用 `--params-file` 传入，避免 Windows 命令行长度限制；支持 UTF-8 BOM。不要向 JSON 中加入上游 URL、凭据或自定义请求头。

## 响应结构

下例按已验证的网关成功响应结构整理，候选及覆盖信息已删减，费用按当前 5 积分登记价格示例填写；数字和版本不表示固定数据集规模，也不代表此次改价已线上验证。脚本把实际费用响应头合入保存的 JSON：

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
          "design_registration_id": "DSR:wipo_hague:EMID.001431738-0001",
          "primary_identifier": "001431738",
          "registration_jurisdiction_code": "EMID",
          "jurisdiction_iso2": "EM",
          "title": "en: Bottles fr: Flacons es: Frascos el: Φιαλίδια",
          "title_en": "Bottles",
          "locarno_classes": ["09-01"],
          "image_score": 0.8597,
          "similarity": 85.97,
          "matched_modality": "image",
          "simple_legal_status": "inactive",
          "registration_date": "2015-03-12",
          "image_available": true,
          "risk_level": "high",
          "risk_reasons": []
        }
      ],
      "coverage": {
        "candidate_unit": "readable_image_media",
        "coverage_ratio": 2.088608,
        "metadata_unknown": {"holder": 9, "legal_status": 4},
        "unresolved_hits": 253,
        "unverified_hits_dropped": 0
      },
      "warnings": ["index_hits_without_profile", "unknown_metadata_retained", "metadata_incomplete", "line_rerank_unavailable"],
      "capability_version": "design_similar_v2.2"
    },
    "usage": {"request_units": 2, "credit_cost": 35, "credit_waived": false}
  },
  "costToken": 9999,
  "costCredit": 5
}
```

外层 `data` 是上游完整 envelope，其中 `data.data` 是业务对象。后端保留动态 Map，公共 HTTP 序列化可能省略对象中值为 null 的字段；缺省与 null 均按来源事实未知处理，不承诺逐字节复现原响应。成功需同时检查 HTTP 2xx、网关 `errcode: 200` 和上游 `data.code: OK`，不能只看 HTTP 200 或进程退出码。来源成功消息实测为 `message: success`。

| 路径 | 类型 | 说明 |
|---|---|---|
| `errcode`, `errmsg` | integer, string | 网关状态与消息；成功为 200，错误保留实际代码和消息 |
| `data` | object | 上游 envelope；错误时可能不存在 |
| `data.code`, `data.message` | string | 上游业务状态与消息；成功 code 为 OK |
| `data.request_id`, `upstreamRequestId` | string | 上游请求标识；后者存在时由后端提取 |
| `data.data` | object | 外观检索业务数据 |
| `data.data.candidates` | object[] | 候选列表；空列表不代表无侵权风险 |
| `data.data.coverage` | object | 来源覆盖信息，字段见下表 |
| `data.data.warnings` | string[] | 来源警告；保留实际内容 |
| `data.data.capability_version` | string | 来源能力/规则版本，不硬编码当前版本 |
| `data.data.asset_code`, `data.data.asset` | string | 来源资产标识，供追溯 |
| `data.data.model_versions` | object | 模态名到模型版本的映射，如 image/text；只展示返回项 |
| `data.data.execution` | object | 引擎、耗时及调试信息，见下表 |
| `data.data.category_filter`, `data.data.risk_adjustment` | object | 来源分类筛选与风险调整元数据，见下表 |
| `data.data.line_rerank` | object | 来源线图重排元数据；未执行或失败时可能缺省，见下表 |
| `data.usage` | object | 来源账户用量，不是用户售价、用户算力或用户余额 |
| `costToken`, `costCredit` | integer | 脚本将 X-Cost-Token / X-Cost-Credit 合入 JSON，响应头优先；费用示例为 9999 / 5。实际以返回头为准，缺失不代表免费 |
| `httpStatus`, `error`, `details` | integer, string, string | 脚本归一化错误时可附加的 HTTP 状态、错误及非 JSON 响应正文；不会因费用字段存在就视为成功 |

### 候选字段

以下是交付约定的 23 个字段及兼容的风险字段。均以 `data.data.candidates[]` 为父路径；字段可能缺省或为 null，不承诺每次全部返回。日期为 YYYY-MM-DD，缺省/null 表示来源未知：

| 字段 | 类型 | 展示语义 |
|---|---|---|
| `design_registration_id` | string | 来源外观登记唯一标识 |
| `primary_identifier` | string | 来源主要检索标识 |
| `application_number` | string | 申请号 |
| `registration_number` | string | 登记号 |
| `publication_number` | string | 公布号 |
| `registration_jurisdiction_code` | string | 来源归属码，如 EMID/USID |
| `jurisdiction_iso2` | string | 来源提供的 ISO 地区字段，不与归属码互换 |
| `title` | string | 原始标题 |
| `title_en` | string | 来源英文标题，不自行补译 |
| `title_language` | string | 原始标题语言，可能为 unknown |
| `title_en_source` | string | 英文标题来源 |
| `holder_names` | string[] | 持有人信息 |
| `designer_names` | string[] | 设计人信息 |
| `locarno_classes` | string[] | 来源洛迦诺分类，缺失为未知 |
| `image_score` | number | 原始图像模态分数 |
| `text_score` | number | 原始文本模态分数；与 image_score 不相加 |
| `similarity` | number | 来源 0–100 百分制分数换算，不是概率，不再次乘以 100 |
| `matched_modality` | string | 本候选匹配模态 |
| `simple_legal_status` | string | 来源法律状态，不自行推断 |
| `registration_date` | string | 登记日期 |
| `application_date` | string | 申请日期 |
| `publication_date` | string | 公布日期 |
| `image_available` | boolean | 来源图片可用提示，不等同于图片 URL |
| `risk_level` | string | 来源规则层风险提示，不构成侵权判定 |
| `risk_reasons` | string[] | 来源规则依据；空数组不等于无风险 |

### 覆盖与处理元数据

下面列出实测嵌套字段；来源可能增加、缺省或置 null，不自行补值。主覆盖字段以 `data.data.coverage` 为父路径：

| 字段 | 类型 | 说明 |
|---|---|---|
| `candidate_total`, `indexed_vectors` | integer | 来源候选单位总数、已索引向量数，不等于本次返回的专利数 |
| `candidate_unit`, `collection_name` | string | 来源计数单位、索引集合标识 |
| `coverage_ratio` | number | 来源定义的比值，实测可大于 1；不能当成 0–1 概率或专利完整覆盖百分比 |
| `unresolved_hits`, `unverified_hits_dropped` | integer | 来源未解析命中数、未经核实而丢弃的命中数 |
| `metadata_unknown` | object | 未知元数据计数，如 locarno_class、holder、registration_jurisdiction_code、legal_status（integer）；不是逐候选判定 |
| `modalities` | object | image/text 等模态的覆盖对象；其 candidate_total、indexed_vectors、candidate_unit、collection_name、coverage_ratio 同上 |

下表路径以 `data.data` 为父路径，属于来源处理过程信息，不在用户主结果中展开内部引擎实现：

| 字段 | 类型 | 说明 |
|---|---|---|
| `execution.engine`, `execution.elapsed_ms` | string, integer | 来源引擎标识、总耗时（毫秒） |
| `execution.timings_ms` | object | 动态调试指标对象；不保证所有值都是耗时 |
| `execution.timings_ms.image_embed_ms`, `image_ann_ms`, `profile_lookup_ms` | integer | 图像编码、向量查询、元数据回查耗时（均相对于 timings_ms） |
| `execution.timings_ms.line_rerank_media_lookup_ms`, `line_rerank_oss_ms`, `line_rerank_embed_ms` | integer | 线图重排的媒体回查、读取、编码耗时（均相对于 timings_ms）；成功执行时按实际返回展示 |
| `execution.timings_ms.ann_prefilter_limit`, `ann_prefilter_codes` | integer, string | 来源预过滤上限、实际预过滤标识 |
| `execution.timings_ms.image_query_is_line_drawing` | boolean | 来源对本次查询图片的线图判断 |
| `execution.timings_ms.milvus_transport`, `line_rerank_error` | string | 来源传输方式、线图重排错误（均相对于 timings_ms）；警告不必然使已返回候选失效 |
| `category_filter.applied`, `dropped`, `query_rerank_promoted` | boolean, integer, integer | 分类筛选是否应用、丢弃数、重排提升数（均相对于 category_filter） |
| `category_filter.anchor_classes`, `query_ref_classes` | string[] | 来源锚点分类、查询参考分类（均相对于 category_filter） |
| `category_filter.non_qref_cap.applied`, `cap`, `dropped` | boolean, integer, integer | 非参考分类候选限制是否应用、上限、丢弃数（均相对于 non_qref_cap） |
| `risk_adjustment.applied`, `version` | boolean, string | 来源风险调整是否应用、规则版本（均相对于 risk_adjustment） |
| `risk_adjustment.same_design_capped`, `category_unknown`, `cross_category`, `same_design_max_seats` | integer | 同设计限制数、分类未知数、跨分类数、同设计最大席位（均相对于 risk_adjustment）；保留来源口径 |
| `line_rerank.applied`, `reranked`, `max_candidates`, `media_missing`, `weight` | boolean, integer, integer, integer, number | 线图重排是否应用、重排数、候选上限、缺媒体数、来源权重（均相对于 line_rerank）；不自行重新加权候选分数 |

`data.usage` 下的实测字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `record_id` | integer | 来源用量记录标识 |
| `request_units`, `credit_cost` | integer, number | 来源请求单位数、来源积分成本，均不代表用户扣费 |
| `credit_waived` | boolean | 来源是否豁免其费用 |
| `remaining_quota`, `remaining_credits` | number | 来源账户额度、积分余额，不展示为用户的 LinkFox 余额 |
| `credit_breakdown` | object | 来源费用明细；cache_discount_applied、scan、model、media、rows、base 为 number，均不是用户售价 |

保持返回顺序，只展示实际返回项；不得臆造图片 URL、覆盖度、持有人、分数或下载链接。当前来源包含 WIPO 海牙非 CN 与 CN 独立范围、EUIPO、USPTO；可用范围与装载缺口按本次 `coverage` / `warnings` 展示，不硬编码历史数量，也不将合法地区参数当成完整覆盖保证。覆盖度无法计算的失败不能解释为零命中。

## 缓存、费用与落盘

- 成功响应按网关、端点、API Key 指纹与完整参数缓存 24h；HTTP/业务失败不缓存。读取前仍要求配置当前 Key，并按其指纹隔离；缓存命中不联网验证 Key 是否仍有效。
- 缓存命中不发新请求，费用字段来自原始响应，不是本次新扣费；`--no-cache` 主动刷新可能再次消耗，继续调用前说明这一点。
- 登记价格为每次新检索 5 积分（￥0.05/次），由网关统一扣费。实际扣费展示以网关费用响应为准；后端成本、来源积分、`usage` 或空费用字段不作为用户扣费金额或免费依据。
- 位置参数 JSON 与 `--params-file <UTF-8 JSON 文件>` 等价；`--inline` 仅控制显示，始终落盘。
- 完整响应保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sif-compliance-detection-<timestamp>.json`。请求前准备最终 session/data 并独占预留唯一文件；SESSION_ID 控制字符、路径字符、Windows 保留名与尾部点/空白均在请求前拒绝。当前目录不可写即报错，不回退家目录或临时目录。
- 小于等于 8 KB 的响应打印全量；更大响应打印摘要和主列表前三条，详见 SKILL.md 的固定输出块。脚本不额外保存请求正文或原始 API Key；实际响应保持完整。

## 错误与失败处理

| 情况 | 处理 |
|---|---|
| 400 / 无效参数 | 展示实际字段错误；不自动改变图片、筛选或候选数 |
| 上游认证错误（如 AUTH_ACCESS_KEY_INVALID）/ 数仓服务凭据未配置 | 联系后端管理员检查上游配置，保留 code/request_id；客户端不索取上游 AccessKey/SecretKey 或门户口令 |
| LinkFox 网关 401 / 402 / 算力或余额不足 | 读取 [onboarding.md](onboarding.md)，按同类 Skill 的统一流程处理用户 Key、认证和算力问题 |
| 403 | 按实际权限错误处理，不绕过授权或索取上游凭据 |
| 3xx | 返回 Redirect blocked，不转发 Key、不跟随重定向 |
| Invalid request header | 环境变量头含控制字符或不能按 Latin-1 编码；只提示头名称，不回显 Key，不发请求。将透传头改成 ASCII 标识后由用户决定后续调用 |
| 5xx / 超时 / 连接中断 | 不自动重试；调用结果可能未知，保留已有请求标识 |
| 上游 code 不是 OK 或响应含 error | 保留业务错误，不缓存、不当成功候选展示 |
| 覆盖度不足或无法建立 | 保留来源失败/警告；不能当作零命中或无侵权结论 |

## curl 示例

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

这是 Bash 的协议示例，`request.json` 按 SKILL.md 示例从真实本地图生成，不使用占位图片地址。curl 本身不提供缓存、自动落盘和费用头合并；正式工作流优先直接入口脚本：`python scripts/ec_dw_design_similar_search.py --params-file request.json [--inline]`。不要再用 curl 重复已由脚本完成的收费请求。

## Feedback API

反馈独立于工具网关：`POST https://skill-api.linkfox.com/api/v1/public/feedback`，Content-Type 为 application/json。

```json
{"skillName":"linkfox-sif-compliance-detection","sentiment":"NEUTRAL","category":"BUG","content":"脱敏后的预期与实际差异"}
```

`sentiment`: POSITIVE/NEUTRAL/NEGATIVE；`category`: BUG/COMPLAINT/SUGGESTION/OTHER。可反馈描述与实际不符、结果偏离用户意图、明确评价或具体改进。只发脱敏摘要，不包含 API Key、上游凭据、图片/Base64 或原始业务行。
