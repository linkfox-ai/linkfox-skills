# linkfox-temu-category-search 子能力归档

以下内容保留该子能力的执行边界、调用规则、参数、响应字段、错误处理和认证引导，执行时以本档案及主 SKILL.md 的路由为准。

## 能力说明与执行规则

---
name: linkfox-temu-category-search
description: 在已同步到本地库的 Temu 类目数据中按关键词检索类目中文名、英文名与类目 id，用于商品/店铺筛选的类目 id。当用户提到 Temu 类目、Temu category id、Temu 类目树、Temu 后台类目、temu 品类、syncTemuCategory（Temu 品类同步）后查询类目、Temu category search 时触发。即使用户未提及工具名，只要在本地已同步的 Temu 类目库里按关键词找类目 id，也应触发此技能。
---

# Temu 类目检索

## 要点

- **必填**：`keyword`（子串匹配类目中文名、英文名、类目 id）。
- **分页**：`page` 从 1 起；`pageSize` 默认 50、最大 200。
- 返回的 **`id` / `categoryId`** 可作为 Temu 商品查询的 `categoryHome`/`categoryBackend`、店铺查询的 `category` 等入参的类目标识（与具体工具 schema 一致即可）。

## MCP 入口

检索与同步均仅通过 `LinkFox` 的 `proxy_call` 执行，精确 `toolName` 见下方【MCP 调用】。

## 参考

入参/出参表见本文件下方的“API 参考”。

## 解决认证和积分问题
发生以下异常情况时，采用 references/onboarding.md 引导解决问题：

### 异常情况
- **MCP 连接或下游响应 401/402**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

## 积分消耗规则

不消耗积分。

## API 参考

# Temu 品类检索 API 参考

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- 检索 **toolName**：`ehunt/temu/temuCategorySearch`
- 同步 **toolName**：`ehunt/temu/syncTemuCategory`
- **arguments**：检索直接使用下表参数对象；同步无业务参数，必须传 `{}`。不得增加 `body`、`data`、`params` 或凭证字段。
- WorkBuddy 自动注入 Authorization；配置和 `arguments` 不得加入 headers、API Key、token、JWT 或手机号。
- 先检查 MCP/schema/`isError`，再读取代理内容；text JSON 只解析一次，最后检查下游 `errcode`、`code`、`errmsg`、`msg`。
- MCP 缺失或失败时停止，不得 HTTP fallback；每一步相同 `toolName + arguments` 不得重复调用，失败、空结果或返回不理想时不得自动重试。
- 检索仅查询已写入本地库的 Temu 品类；必要时先同步，成功后再执行一次检索。本地检索不计费。

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
| categories[].id | string | 类目 id |
| categories[].categoryId | string | 类目 ID（上游 category id） |
| categories[].parentId | string | 父类目 id（顶级为空串） |
| categories[].level | integer | 类目层级 |
| categories[].categoryName | string | 类目名称（中文） |
| categories[].categoryNameEn | string | 类目名称（英文） |
| categories[].isDeleted | integer | 是否已删除：0=正常，1=已删除 |
| categories[].hasChildren | boolean | 是否有子类目 |

## 同步类目（前置）

类目数据须先由该 operation 拉取分类树写入本地库，否则检索结果可能为空。同步会改变本地类目数据状态，仅在空结果且用户确实需要继续定位类目时执行；同步成功后重新检索一次，不循环同步或轮询。

- **toolName**：`ehunt/temu/syncTemuCategory`
- **arguments**：`{}`

### 同步响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| result | 来源未说明 | 成功值为 `success` |
| totalRows | 来源未说明 | 同步写入的类目行数 |

### 同步 MCP 调用示例

```json
{
  "toolName": "ehunt/temu/syncTemuCategory",
  "arguments": {}
}
```

## 检索 MCP 调用示例

```json
{
  "toolName": "ehunt/temu/temuCategorySearch",
  "arguments": {
    "keyword": "kitchen",
    "page": 1,
    "pageSize": 50
  }
}
```

## Feedback API

> 与上方工具网关 API 独立，勿混用 Base URL。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-temu-category-search",
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

## 认证与积分引导

# 解决认证和积分问题

读取 `references/onboarding.md` 并分层处理 MCP 连接、代理层和下游业务错误。WorkBuddy 自动注入 Authorization；不得要求用户提供凭证。下游 402 引导访问 `https://agent.linkfox.com/`，不得自动选套餐、下单、支付或轮询；403 不归入认证或计费错误。
