# `linkfox-etsy-category-search` 参考

## 能力说明

按关键词检索已同步的 Etsy 类目库，返回类目名称、层级、`id`、规范父类目和完整父类目链。返回的 `id` 可作为商品或店铺筛选的 `category` 入参，但必须遵循目标查询接口的参数约束。

## 能力边界与特殊规则

- 必须提供 `keyword`；匹配类目名称、类目 `id` 和 `parentIds` 的子串。
- 只查询已写入 MCP 库的类目；数据需要先由 `_ehunt_syncEtsyCategory` 完成同步。本参考仅覆盖查询，不提供同步脚本。
- `page` 从 1 开始，`pageSize` 默认 50，范围为 1~200。
- 这是本地/已同步库检索，响应的 `costToken` 通常为 0，不应把它当作远端商品或店铺筛选。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`ehunt/etsy/etsyCategorySearch`
- **arguments**：直接使用下表请求参数对象，不增加 `body`、`data`、`params` 或凭证字段。
- WorkBuddy 自动注入 Authorization；配置和 `arguments` 不得加入 headers、API Key、token、JWT 或手机号。
- 先检查 MCP/schema/`isError`，再读取代理内容；text JSON 只解析一次，最后检查下游 `errcode`、`code`、`errmsg`。
- MCP 缺失或失败时停止，不得 HTTP fallback；相同 `toolName + arguments` 不得重复收费调用，失败、空结果或返回不理想时不得自动重试。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `keyword` | string，最大 200 | 是 | 匹配名称、`id`、`parentIds` 的子串 |
| `page` | integer，≥1 | 否 | 页码，默认 1 |
| `pageSize` | integer，1~200 | 否 | 每页条数，默认 50 |

示例：

```json
{"keyword":"jewelry","page":1,"pageSize":50}
```

### 响应字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `total` | integer | 本页返回条数 |
| `costToken` | integer | 消耗 token（本地检索不计费） |
| `categories` | array | 匹配的品类列表 |
| `title` | string | 标题 |

`categories[]`：

| 字段 | 类型 | 说明 |
|---|---|---|
| `categories[].categoryLevel` | integer | 类目层级 |
| `categories[].id` | string | 类目 id |
| `categories[].name` | string | 类目名称 |
| `categories[].parentId` | string | 规范主父类目 id |
| `categories[].parentIds` | string | 全部非空父类目 id（逗号分隔） |

## MCP 调用示例

```json
{
  "toolName": "ehunt/etsy/etsyCategorySearch",
  "arguments": {
    "keyword": "jewelry",
    "page": 1,
    "pageSize": 50
  }
}
```

## 错误和展示

类目库未同步时的空结果要提示同步前置条件；`keyword` 为空、页码小于 1、`pageSize` 越界时提示修正参数。展示时优先给出 `name`、`id`、层级和父类目链，并明确这些数据来自已同步库。认证或计费异常读取 `references/onboarding.md`。

## 积分

不消耗积分；若后续根据类目 ID 调用商品或店铺查询，应按后续接口的返回条数规则单独提示费用。
