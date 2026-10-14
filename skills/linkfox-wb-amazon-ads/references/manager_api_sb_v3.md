# Sponsored Brands V3 Legacy API

来源：`skills/linkfox-amazon-ads-manager/references/api/sb-v3.md`。V3 仅用于已确认的 Legacy Campaign；共存规则见 `manager_api_sb_coexistence.md`。

## MCP 调用

使用 `LinkFox.proxy_call`，精确 `toolName=amazonAds/developerProxy`。直接传 developerProxy 路由对象，WorkBuddy 自动授权，禁止 headers、token 和 HTTP fallback。

```json
{"toolName":"amazonAds/developerProxy","arguments":{"region":"NA","profileId":1234567890,"path":"sb/campaigns","method":"GET","body":"","contentType":"application/json"}}
```

## 路径与方法

| 资源 | list | create | update |
|---|---|---|---|
| Campaign | `GET sb/campaigns` | `POST sb/campaigns` | `PUT sb/campaigns` |
| Ad Group | `GET sb/adGroups` | 来源未说明 | 来源未说明 |
| Keyword | `GET sb/keywords` | `POST sb/keywords` | `PUT sb/keywords` |
| Target | `POST sb/targets/list` | `POST sb/targets` | `PUT sb/targets` |

V3 Creative 位于 Campaign payload 内，没有独立 V3 Creative CRUD。Keyword/Target 单次写入最多 100 个。GET list 的过滤条件必须按 Amazon 原生 query string 传递；Target list 使用 Amazon 原生 `filters[]` body。

旧 caller 的本地结构拦截、宽容过滤器映射、自动分页和逗号拼接不属于 MCP。调用 V3 前由 Agent 使用 V4 Campaign 查询结果确认不是 Multi-Ad-Group；无法确认则不要执行 V3 写操作。

## 响应字段

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | Amazon 下游 HTTP 状态 |
| `body` | string/object | Amazon 原始响应体；完整嵌套属性来源未说明 |
| `error` | string | 失败时的错误摘要 |
| `details` | string/object | 错误详情；内部结构来源未说明 |
