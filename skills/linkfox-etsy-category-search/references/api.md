# `_ehunt_etsyCategorySearch` API 参考

## 调用说明

- **工具名**：`_ehunt_etsyCategorySearch`（LinkFox MCP，`serverName`：第三方数据服务）。
- **MCP 展示名**：Etsy品类查询。
- **数据范围**：查询已写入 MCP 库的 Etsy 品类；库内数据需先通过 **`_ehunt_syncEtsyCategory`**（MCP 展示名：Etsy品类同步）完成同步。

## 请求参数（JSON）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string, maxLen=200 | **是** | 关键词：匹配品类名称、类目 id、parentIds 字段（子串） |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~200，默认 50 | 否 | 每页条数，最大 200 |

## 响应主要字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 本页返回条数 |
| costToken | integer | 消耗 token（本地检索不计费） |
| categories | array | 匹配的品类列表 |
| title | string | 标题 |

### `categories[]` 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| categoryLevel | integer | 类目层级 |
| id | string | 类目 id |
| name | string | 类目名称 |
| parentId | string | 规范主父类目 id |
| parentIds | string | 全部非空父类目 id（逗号分隔） |

## 脚本调试（可选）

仓库内提供 **`scripts/etsy_category_search.py`**（Python 3，仅标准库）。

- **默认路径段**：`ehunt/etsy/etsyCategorySearch`（可用 `LINKFOX_EHUNT_ETSY_CATEGORY_SEARCH_PATH` 覆盖）
- **网关**：`https://tool-gateway.linkfox.com`（可用 `LINKFOX_TOOL_GATEWAY_BASE` 覆盖）；**鉴权**：`LINKFOXAGENT_API_KEY`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

```bash
export LINKFOXAGENT_API_KEY="<your-key>"
python scripts/etsy_category_search.py '{"keyword": "jewelry", "page": 1, "pageSize": 50}'
```

类目数据须先由 **`_ehunt_syncEtsyCategory`** 同步到 MCP 库，否则结果可能为空。
