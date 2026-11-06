# Temu 全球站商品管理接口说明

24 个商品管理操作的独立定义见下表；加签文件下载在本文定义。每个操作使用同一网关，转发 path 为 `/openapi/router`，由 type 区分。

| 操作 | 文档 |
|------|------|
| `bg.local.goods.category.check` | [apis/bg-local-goods-category-check.md](apis/bg-local-goods-category-check.md) |
| `bg.local.goods.compliance.edit` | [apis/bg-local-goods-compliance-edit.md](apis/bg-local-goods-compliance-edit.md) |
| `bg.local.compliance.goods.list.query` | [apis/bg-local-compliance-goods-list-query.md](apis/bg-local-compliance-goods-list-query.md) |
| `bg.local.goods.detail.query` | [apis/bg-local-goods-detail-query.md](apis/bg-local-goods-detail-query.md) |
| `temu.local.goods.delete` | [apis/temu-local-goods-delete.md](apis/temu-local-goods-delete.md) |
| `temu.local.goods.list.retrieve` | [apis/temu-local-goods-list-retrieve.md](apis/temu-local-goods-list-retrieve.md) |
| `bg.local.goods.update` | [apis/bg-local-goods-update.md](apis/bg-local-goods-update.md) |
| `bg.local.goods.list.query` | [apis/bg-local-goods-list-query.md](apis/bg-local-goods-list-query.md) |
| `bg.local.goods.out.sn.set` | [apis/bg-local-goods-out-sn-set.md](apis/bg-local-goods-out-sn-set.md) |
| `bg.local.goods.partial.update` | [apis/bg-local-goods-partial-update.md](apis/bg-local-goods-partial-update.md) |
| `temu.local.goods.pre.sale.status.edit` | [apis/temu-local-goods-pre-sale-status-edit.md](apis/temu-local-goods-pre-sale-status-edit.md) |
| `bg.local.goods.property.get` | [apis/bg-local-goods-property-get.md](apis/bg-local-goods-property-get.md) |
| `bg.local.goods.property.relations` | [apis/bg-local-goods-property-relations.md](apis/bg-local-goods-property-relations.md) |
| `bg.local.goods.property.relations.level.template` | [apis/bg-local-goods-property-relations-level-template.md](apis/bg-local-goods-property-relations-level-template.md) |
| `bg.local.goods.property.relations.template` | [apis/bg-local-goods-property-relations-template.md](apis/bg-local-goods-property-relations-template.md) |
| `bg.local.goods.publish.status.get` | [apis/bg-local-goods-publish-status-get.md](apis/bg-local-goods-publish-status-get.md) |
| `bg.local.goods.sale.status.set` | [apis/bg-local-goods-sale-status-set.md](apis/bg-local-goods-sale-status-set.md) |
| `bg.local.goods.sku.list.query` | [apis/bg-local-goods-sku-list-query.md](apis/bg-local-goods-sku-list-query.md) |
| `temu.local.sku.list.retrieve` | [apis/temu-local-sku-list-retrieve.md](apis/temu-local-sku-list-retrieve.md) |
| `bg.local.goods.sku.out.sn.set` | [apis/bg-local-goods-sku-out-sn-set.md](apis/bg-local-goods-sku-out-sn-set.md) |
| `temu.local.goods.sku.stock.query` | [apis/temu-local-goods-sku-stock-query.md](apis/temu-local-goods-sku-stock-query.md) |
| `temu.local.goods.spec.info.get` | [apis/temu-local-goods-spec-info-get.md](apis/temu-local-goods-spec-info-get.md) |
| `bg.local.goods.stock.edit` | [apis/bg-local-goods-stock-edit.md](apis/bg-local-goods-stock-edit.md) |
| `bg.local.goods.videocoverimage.get` | [apis/bg-local-goods-videocoverimage-get.md](apis/bg-local-goods-videocoverimage-get.md) |


[官方目录](partner-global-catalog.md) · [授权说明](access-token.md) · [分组索引](apis/README.md)

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

## 运行约定

### 认证与地址兼容

| 项目 | 约定 |
|------|------|
| 网关根地址 | LINKFOX_TOOL_GATEWAY → TEMU_API_BASE_URL → STORE_API_BASE_URL → https://tool-gateway.linkfox.com；去除尾斜杠。 |
| 双请求头 | Authorization 与 Token 同值，保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。 |
| JSON 密钥优先级 | token → linkfoxToken → linkfox_token → LINKFOX_AGENT_API_KEY → LINKFOXAGENT_API_KEY。 |
| Global 默认值 | site=global、managementType=semi-managed、tokenPurpose=product-inventory。 |
| 本地令牌 | accessToken 优先；否则精确匹配 storeKey + site + managementType + tokenPurpose，不借用其他区域或用途的令牌。默认文件 ~/.linkfox/temu-access-tokens.json，TEMU_TOKEN_STORE_PATH 可覆盖。 |
| 授权 | 无自动 OAuth；在 Temu 卖家后台选择酷鸟卖家助手 / Cyber-ERP酷鸟助手 / Cyber-ERP，按店铺与用途复制令牌。商品库存与订单发货授权分开；需主账号权限、有效 Token、对应区域授权及紫鸟 IP 白名单。详见 [授权流程](authorization-flow.md)。 |
| 跨域边界 | 首次发品用 linkfox-temu-add-product-us；促销、价格、广告、订单、履约、取消使用各自技能。复用其他域的 Global 场景须显式传 site=global，不能因名称相近使用 US/EU Token。 |

### CLI、缓存与输出

| 入口 / 选项 | 约定 |
|------|------|
| global_manage_*.py | `python scripts/<脚本>.py '<JSON 参数>' [--inline] [--no-cache]`，固定对应 type。业务字段可置顶层或 params 对象，params 对象优先，保持 request 原始层级。 |
| temu_global_proxy.py | 接受 type 与 JSON 业务参数，默认 Global 半托管与 product-inventory；仅将本技能有定义的操作视为已说明能力。 |
| temu_proxy.py | 多站点兼容入口，显式要求 site、managementType、type；site 支持 cn / partner / us / global / eu，managementType 支持 full-managed / semi-managed。params 若非空必须是对象。 |
| temu_global_file_download.py / temu_file_download.py | 下载返回网关 JSON；不会自动将远程文件保存为素材。Global 包装补默认值，通用入口显式要求 site、managementType。 |
| check_linkfox_token.py | 在 /temu/proxy 发送 cn/full-managed、accessToken=probe、type=probe 的最小探测，识别“无法识别当前用户”或“重新登录”。ok 仅表示此探测未命中上述鉴权提示，不能证明店铺授权或真实业务成功；不应无条件先探测再调用。 |
| temu_token_guide.py | 本地输出授权步骤；支持 shopType（兼容 managementType）、tokenPurpose、site，不发送请求。 |
| save_temu_access_token.py | 本地保存 storeKey、site、managementType、tokenPurpose、accessToken，可附 label；同一组合替换，其他组合保留。 |
| list_temu_access_tokens.py | 默认脱敏，JSON mask=false 时返回完整令牌。 |
| get_temu_access_token.py | 按精确组合读取；tokenPurpose 默认 default，Global API 包装默认 product-inventory，调用者应据保存用途传值。 |
| 缓存 | 本技能不使用响应缓存，所有业务调用 run 均加 --no-cache；公共调用器可能建立空的缓存目录，不读取或保存响应缓存，也没有第二层缓存。 |
| 落盘 | 业务包装强制使用可写 cwd/linkfox；禁止回退 /tmp、家目录或其他工作区；不可写即报错。每次调用用微秒文件名保留完整响应，按 SESSION_ID 聚合。接口标识去除 type 的公共前缀，超长标识使用截断加摘要以兼容 Windows 文件路径；保存失败明确报错。 |
| 输出 | body 为合法 JSON 字符串时附加 temuBody，保留 body 原文；不超过 8000 UTF-8 字节完整打印，超过时给摘要及最大列表前三条；--inline 强制全量。原样保存错误，不自动重试写操作。 |

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | Global 脚本默认 global；多站点兼容入口显式传入，须与令牌匹配。 |
| managementType | string | 是 | Global 脚本默认 semi-managed；通用入口支持 full-managed / semi-managed。 |
| accessToken | string | 是 | Temu 店铺令牌，可由本地 storeKey 匹配后填入。 |
| url | string | 是 | 原始加签文件 URL，保留查询串与编码，不自行拆解签名。 |

#### 仅脚本使用的兼容字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| storeKey | string | 与 accessToken 二选一 | 本地店铺键；结合 site、managementType、tokenPurpose 精确读取。 |
| tokenPurpose | string | 否 | Global 包装默认 product-inventory；通用入口默认 default。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥，按所列顺序优先于环境变量，不进入 Body。 |
| --inline | CLI flag | 否 | 完整打印并保存。 |
| --no-cache | CLI flag | 否 | 包装始终关闭响应缓存，不读写响应缓存。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 按公共规则解释外层网关状态。 |
| errmsg | string | 网关错误消息。 |
| code | integer | 网关错误码 1002（参数或用户 Token 无效）、1003（转发失败）。 |
| 其他原始字段 | 未明确 | 下载结果子字段的名称和类型未明确；脚本完整保存、返回网关 JSON，不补造文件内容、文件地址或文件名字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- code=1002 时检查参数和 LinkFox 用户令牌；1003 时检查 Temu 店铺令牌、加签 URL、IP 白名单与转发信息。返回 JSON 不等同于素材已下载到本地。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"global","managementType":"semi-managed","accessToken":"TOKEN","url":"https://example.com/signed-file-url"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-manage-product-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
