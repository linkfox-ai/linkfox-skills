# 官方模板：listOfficialTemplates

**接口**：`POST /agent-studio/table-template/list`，查询已发布、未删除的官方模板。

使用 `LINKFOX_AGENT_USER_API_URL`，默认 `https://agent-api.linkfox.com`。这是公开 Agent 接口，不需要 API Key；其他表格接口的地址与鉴权保持原样。

## 调用

```bash
python scripts/smart_table.py listOfficialTemplates
python scripts/smart_table.py listOfficialTemplates '{"keyword":"选品","page":1,"pageSize":24}'
python scripts/smart_table.py listOfficialTemplates '{"templateType":"table","platform":"amazon","stage":"selection","page":1,"pageSize":24}'
python scripts/smart_table.py listOfficialTemplates '{"id":"<列表返回的 32 字符模板 ID>"}' --inline
```

参数省略等价于 `{}`，也支持 `list-official-templates`。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 具体传值与约束 |
|---|---|---|---|---|
| id | string | 否 | 不筛选 | 从本接口 `list[].id` 取真实的 32 字符模板 ID，trim 后精确匹配；不是 notebookId / tableId，不要自己编造 |
| templateType | string | 否 | `table` | `table` = 多维表格模板，`app` = 应用模板，`all` = 所有类型。省略、`null` 或空白时通常查询 `table`；**传了非空 id 且类型省略、为 null 或空白时查询所有类型** |
| platform | string | 否 | 不筛选 | 单选：`amazon` = 亚马逊，`walmart` = 沃尔玛，`tiktok` = TikTok，`ozon` = Ozon。省略、`null`、`""` 或纯空白表示不限；非空 trim 后精确匹配，最多 64 个字符 |
| stage | string | 否 | 不筛选 | 单选：`selection` = 选品，`procurement` = 采购，`listing` = 上架，`fulfillment` = 履约。省略、`null`、`""` 或纯空白表示不限；非空 trim 后精确匹配，最多 64 个字符 |
| categoryId | string | 否 | 不筛选 | 分类真实 ID，可取列表模板的 `categoryIds[]` 中一项；传一个 ID，不传分类名称或数组。省略、`null` 或空白查询全部分类 |
| keyword | string | 否 | 不筛选 | 自由文本，例如 `"选品"`、`"库存"`；trim 后匹配名称或简介。省略、`null` 或空白不限制关键词 |
| page | integer | 否 | 1 | JSON 整数，例如 `1`、`2`；≥ 1，不传 `"1"` 或布尔值。`null` 使用默认值；后端最大页码 42949672，超过按上限处理 |
| pageSize | integer | 否 | 12 | JSON 整数，1–50，例如 `12`、`24`、`50`；`null` 使用默认值；不是 perPage |

平台和阶段传上表的小写编码，不传中文标签、数组或逗号拼接的多个值。**这两个字段的 `all` 没有特殊含义，不代表不限**，查询不限平台 / 阶段时省略字段或传 `""`。

上表列出当前前端配置的具体选项。后端对 `platform`、`stage` 和 `templateType` 不设置选项白名单，其他非空字符串也会按配置原值精确筛选；平台 / 阶段长度超过 64 个字符时后端返回 400。脚本透传字符串，不把当前选项写死成永久枚举。

所有筛选按 AND 组合，包括按 id 查询时额外传入的平台、阶段、类型、分类和关键词。只按 ID 获取详情时只传 `id`，避免保留筛选条件导致空结果。空串不表示“只查未配置平台 / 阶段”，而是完全不加该筛选。

### 组合示例

```bash
# 亚马逊选品阶段的多维表格模板
python scripts/smart_table.py listOfficialTemplates '{"templateType":"table","platform":"amazon","stage":"selection","page":1,"pageSize":24}'

# TikTok 上架阶段的应用模板
python scripts/smart_table.py listOfficialTemplates '{"templateType":"app","platform":"tiktok","stage":"listing","page":1,"pageSize":12}'

# 不限类型、不限平台，只看履约阶段
python scripts/smart_table.py listOfficialTemplates '{"templateType":"all","platform":"","stage":"fulfillment"}'

# 清空平台和阶段筛选，按关键词查询第 2 页
python scripts/smart_table.py listOfficialTemplates '{"platform":"","stage":"","keyword":"库存","page":2,"pageSize":24}'
```

## 响应

顶层为 `list / total / page / pageSize`。`list` 中包含模板的 `id`、`name`、`intro`、`templateType`、`platform`、`stage`、`shareUrl`、`coverUrl`、`categoryIds`、`resourceId`、`tutorialUrl`、`detailImages`、`description`、`sortOrder`、`viewCount`、`usageCount`、`createdAt`、`updatedAt`。`platform` / `stage` 返回模板配置的编码，未配置返回空串。

此公开接口成功时 `errcode` 可省略、为 `0` 或 `200`，同时必须有数组 `list`；空数组表示没有匹配模板。错误读取 `errmsg`，网络错误也可能是 `errcode: 0`，不能仅看错误码。

完整响应始终落盘到会话 `data/`。UTF-8 响应 ≤ 8000 字节时全量打印，超过时打印分页与前三条模板摘要；`--inline` 强制全量打印。参数错误在请求前拦截，HTTP、网络和响应解析错误返回结构化信息。
