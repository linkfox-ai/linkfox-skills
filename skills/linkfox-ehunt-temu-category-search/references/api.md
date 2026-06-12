# EHunt Temu 品类检索 API 参考

## 调用说明

- **网关路由**：`POST ehunt/temu/temuCategorySearch`（完整：`https://tool-gateway.linkfox.com/ehunt/temu/temuCategorySearch`）。
- **MCP 展示名**：Temu 品类查询（确切工具名以当前环境下发的工具元数据为准）。
- **鉴权**：请求头 `Authorization: <LINKFOXAGENT_API_KEY>`。
- **数据范围**：查询已写入本地库的 EHunt Temu 品类；库内数据需先通过 **`ehunt/temu/syncTemuCategory`**（MCP 展示名：Temu 品类同步）完成同步。本地检索不计费。

## 请求参数（JSON）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string, maxLen=200 | **是** | 关键词：匹配类目中文名、英文名、类目 id（子串） |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~200，默认 50 | 否 | 每页条数，最大 200 |

## 响应主要字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 本页返回条数 |
| categories | array | 匹配的品类列表 |
| title | string | 标题（`Temu 品类检索`） |

### `categories[]` 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 类目 id |
| categoryId | string | 类目 ID（上游 category id） |
| parentId | string | 父类目 id（顶级为空串） |
| level | integer | 类目层级 |
| categoryName | string | 类目名称（中文） |
| categoryNameEn | string | 类目名称（英文） |
| isDeleted | integer | 是否已删除：0=正常，1=已删除 |
| hasChildren | boolean | 是否有子类目 |

## 同步类目（前置）

类目数据须先由 **`ehunt/temu/syncTemuCategory`**（MCP 展示名：Temu 品类同步，无入参）拉取分类树写入本地库，否则检索结果可能为空。其返回 `result`（成功为 `success`）与 `totalRows`（同步写入的类目行数）。

## 脚本调试（可选）

仓库内提供 **`scripts/ehunt_temu_category_search.py`**（Python 3，仅标准库）。

- **网关**：`https://tool-gateway.linkfox.com`（可用 `LINKFOX_TOOL_GATEWAY_BASE` 覆盖）
- **默认路径段**：`ehunt/temu/temuCategorySearch`（可用 `LINKFOX_EHUNT_TEMU_CATEGORY_SEARCH_PATH` 覆盖）
- **鉴权**：`LINKFOXAGENT_API_KEY`（申请见 https://skill.linkfox.com/linkfoxskills/guide.htm ）

```bash
export LINKFOXAGENT_API_KEY="<your-key>"
python scripts/ehunt_temu_category_search.py '{"keyword": "kitchen", "page": 1, "pageSize": 50}'
```

类目数据须先由 **`ehunt/temu/syncTemuCategory`** 同步到本地库，否则结果可能为空。

## Feedback API

> 与上方工具网关 API 独立，勿混用 Base URL。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-ehunt-temu-category-search",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: 使用本 skill YAML frontmatter 中的 `name`
- `sentiment`: `POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`: `BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
- `content`: 简述用户意图、实际结果与问题或好评原因
