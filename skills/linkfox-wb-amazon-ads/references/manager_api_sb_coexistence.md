# Sponsored Brands V3 / V4 共存与路由

来源：`skills/linkfox-amazon-ads-manager/references/api/sb-coexistence.md`。

## MCP 调用

使用 `LinkFox.proxy_call`，精确 `toolName=amazonAds/developerProxy`。WorkBuddy 自动授权；禁止 headers、token 和 HTTP fallback。响应按 `manager_api.md` 的 developerProxy 包装处理。

## 版本边界

| 场景 | 选择 |
|---|---|
| 新建 Campaign、多 Ad Group、Ad、独立 Creative | V4 |
| 已确认的 Legacy Campaign | 可使用 V3 |
| Keyword / Target | 默认按 V4 业务意图，但 Amazon 路径仍是共享 `sb/keywords`、`sb/targets[/list]` |
| 版本调用失败 | 返回原错误，不自动改版本重试 |

Campaign、Ad Group、Ad 的 V4 路径为 `sb/v4/campaigns/**`、`sb/v4/adGroups/**`、`sb/v4/ads/**`。Amazon 不存在 `sb/v4/keywords`、`sb/v4/targets` 或独立 `sb/v3/creatives` 路径。

来源旧 caller 会用本地参数拦截 Multi-Ad-Group V3 调用，但该拦截器已删除。现在应先通过 V4 Campaign 查询结果读取 `isMultiAdGroupsEnabled` 等实际结构证据；如果来源响应没有该字段或结构无法确认，标记“来源未说明”并停止 V3 写操作，不得伪造本地错误对象。

## 决策流程

```text
新建 / 多 Ad Group / Ad / Creative -> V4
Keyword / Target -> V4 业务意图 + Amazon 共享 targeting 路径
已确认 Legacy -> 可用 V3
V3 + Multi-Ad-Group 或结构不明 -> 停止
任一失败 -> 保留原错误，不自动回落
```

## 响应字段

本 reference 不新增业务响应字段。`developerProxy` 使用与 `manager_api.md` 相同的包装：

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | 下游 Amazon HTTP 状态；来源明确出现 |
| `body` | string/object | Amazon 原始响应体；完整嵌套属性来源未说明 |
| `error` | string | 代理错误摘要；失败时可能出现 |
| `details` | string/object | 错误详情；来源未说明固定内部结构 |
