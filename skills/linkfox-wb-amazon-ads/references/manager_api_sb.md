# Sponsored Brands API 索引

来源：`skills/linkfox-amazon-ads-manager/references/api/sb.md` 及其 V3、V4、共存 reference。

## MCP 调用

统一使用 `LinkFox.proxy_call`，精确 `toolName=amazonAds/developerProxy`；参数和响应包装见 `manager_api.md`。WorkBuddy 自动授权，禁止 headers、token 和 HTTP fallback。

```json
{"toolName":"amazonAds/developerProxy","arguments":{"region":"NA","profileId":1234567890,"path":"sb/v4/campaigns/list","method":"POST","body":"{}","contentType":"application/vnd.sbcampaignresource.v4+json"}}
```

## 版本选择

| 版本 | 适用范围 | reference |
|---|---|---|
| V4 | 默认；新建 Campaign、多 Ad Group、Ad、独立 Creative | `manager_api_sb_v4.md` |
| V3 | 仅已确认的 Legacy Campaign | `manager_api_sb_v3.md` |
| 共享 targeting | Keyword / Target 仍使用 `sb/keywords`、`sb/targets[/list]` | `manager_api_sb_coexistence.md` |

不得在失败时从 V4 自动回落 V3。写操作必须先确认；相同调用不重复执行。

## 响应字段

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | Amazon 下游 HTTP 状态 |
| `body` | string/object | Amazon 原始响应体；完整嵌套属性来源未说明 |
| `error` | string | 失败时的错误摘要 |
| `details` | string/object | 错误详情；内部结构来源未说明 |
