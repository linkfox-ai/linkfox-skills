# Temu 美国站发货与物流履约 接口说明

27 个履约操作各有独立文档，见 [接口索引](apis/README.md)；每个操作通过 `/temu/proxy` 的 `type` 标识转发至美国站 `/openapi/router`。加签文件下载在本文件定义，共 28 个操作；待接入目录项不计入。

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

### 认证与路由兼容

- 请求基础地址优先使用 `LINKFOX_TOOL_GATEWAY`，其次 `TEMU_API_BASE_URL`、`STORE_API_BASE_URL`，最后默认网关；去掉尾部 `/`。
- 业务封装的 LinkFox 密钥优先级为 JSON `token`、`linkfoxToken`、`linkfox_token`，再到 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY`。保留 `Authorization` 与 `Token` 同值双头以及 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 上下文头。
- Temu `accessToken` 显式提供时优先，否则按 `storeKey + site + managementType + tokenPurpose` 精确读取本地存储。默认位置 `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖，不跨店铺或用途回退。详见 [access-token.md](access-token.md) 与 [authorization-flow.md](authorization-flow.md)。
- 美国站入口默认 `site=us`、`managementType=semi-managed`；按 storeKey 选择令牌时默认 `tokenPurpose=order-shipping`。无论是否显式指定用途，代理和下载均用与请求相同的规范化站点和托管类型精确查找令牌。`temu_proxy.py`、`temu_file_download.py` 要求显式站点与托管类型；本地令牌工具的用途默认 `default`。
- 美国站代理的显式 `params` 对象优先；否则将非保留顶层业务字段收集为 params。保留键为 `token`、`linkfoxToken`、`linkfox_token`、`accessToken`、`storeKey`、`site`、`managementType`、`tokenPurpose`、`type`、`params`。不会自动增加 request 层级。通用 `temu_proxy.py` 仅转发显式 params 对象，非对象报错。
- 所有业务 LinkFox 请求经 `call_api.run`，超时默认 150 秒；封装接受自定义 timeout 参数。业务适配层负责双认证头、上述密钥优先级、网关地址覆盖与错误解析。

### CLI、缓存与输出

| 入口或选项 | 约定 |
|---|---|
| `python scripts/us_*.py '<JSON>' [--inline] [--no-cache]` | 27 个专用入口保留，内部统一走 `_us_fulfillment_script.run_cli`。 |
| `temu_us_proxy.py` / `temu_us_file_download.py` | 美国站通用代理及加签下载，沿用相同 JSON 与选项格式。 |
| `temu_proxy.py` / `temu_file_download.py` | 通用兼容入口；参数字段与校验见各业务说明。 |
| `--inline` | 始终保存完整 JSON，同时强制完整打印。否则大于 8000 字节仅打印摘要和最大列表前三条。 |
| `--no-cache` | 业务脚本无响应缓存；内部调用 run 始终携带此选项，既不读也不写响应缓存。 |
| 输出路径 | 仅 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-fulfillment-us-<timestamp>.json`；SESSION_ID 聚合同一任务，缺省生成会话号。 |
| 不可写目录 | 请求前检查 cwd/linkfox，不回退到家目录、ACPX_WORKSPACES 或临时目录；写入失败明确报错。 |

公共调用器的中间打印和落盘由业务适配层接管，完整结果（含解析后的 temuBody）由业务输出层保存一次。同时保存会话 `_meta.json`、`index.jsonl` 和数据文件记录。无请求重试、自动翻页或后台轮询。

`check_linkfox_token.py` 提供最小代理探测 CLI，使用 `/temu/proxy`，不属于额外业务操作；它会发送真实请求，仅在用户需要诊断且具备相应授权时使用，不作为本地依赖检查。该探测只根据“无法识别当前用户/重新登录”消息识别认证问题；不能据它的 ok=true 推断店铺授权或余额正常，仍按公共规则检查实际响应。

### 网关请求及响应

代理操作的完整网关参数、业务字段、Temu 嵌套结构和错误码在各自接口文档独立维护。处理顺序为外层 HTTP / errcode → 网关 code → 解析 body → Temu success / errorCode / errorMsg / result。原始 body 始终保留，只有合法 JSON 字符串才增加 temuBody；不补造缺失结果。

## 接口：加签文件下载（fileDownload）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| site | string | 是 | 美国站脚本默认 `us`；通用入口须显式传入并校验 `cn` / `partner` / `us` / `global` / `eu`。 |
| managementType | string | 是 | 美国站脚本默认 `semi-managed`；通用入口须显式传入 `semi-managed` / `full-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，实际网关 Body 必传；显式值优先。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地查令牌，不发送给网关。须与站点、托管类型及用途精确匹配。 |
| tokenPurpose | string | 否 | 美国站本地选令牌默认 `order-shipping`，通用入口默认 `default`；不发送给网关。 |
| url | string | 是 | 面单或 Scan Form 文档接口返回的加签资源地址；脚本返回网关 JSON，不擅自假定响应为 PDF 二进制或固定 Base64 字段。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥兼容别名与优先级见运行约定。 |
| --inline / --no-cache | CLI flag | 否 | 完整打印 / 显式禁用缓存；业务封装始终禁用缓存。 |

实际网关 Body 仅包含 `site`、`managementType`、`accessToken`、`url`。须使用对应店铺和站点获取的有效文档 URL；失效后重新调用返回该链接的文档接口，按调用约束处理。美国站下载脚本使用 storeKey 时同样应用美国站默认值，并按完整组合精确查找令牌，不跨店铺、站点或用途回退。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| _http_status | integer / null | 脚本本地诊断字段，记录本次真实 HTTP 状态；连接失败时为 null，不是网关保证字段。先按此判断 HTTP 结果，401/402 转入 onboarding 引导，不以正文中的成功字段覆盖。 |
| _raw_response | 以实际响应为准 | 仅当响应根不是对象，或上游已有同名 _http_status 时，脚本将完整原响应放在此字段，并在外层记录真实状态；此时从原响应读取业务内容。 |
| errcode | integer / string / null | 若返回，按公共规则判断。 |
| errmsg | string | 若返回，错误或结果消息。 |
| code | integer | 若返回，`1002` 参数/Token 问题，`1003` 转发失败。 |
| 其他网关字段 | 以实际响应为准 | 文件数据字段以实际响应为准；下载入口完整保留 JSON，不自动增加 temuBody，不补造文件内容字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `1002` 检查参数与 LinkFox Token；`1003` 检查 Temu 令牌、用途、白名单及资源 URL。下载是否完成依据实际网关返回内容，不仅依据 HTTP 成功。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"us","managementType":"semi-managed","accessToken":"TOKEN","url":"https://example.com/signed-file-url"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-fulfillment-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
