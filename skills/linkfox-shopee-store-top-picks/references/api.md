# linkfox-shopee-store-top-picks — 参数与字段参考

Shopee **Top Picks 模块**全部 4 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.top_picks.get_top_picks_list](https://open.shopee.com/documents/v2/v2.top_picks.get_top_picks_list?module=100&type=1)

## 通用约定

- **path**：须 `api/v2/top_picks/...`
- **标识**：通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.top_picks.{api}?module=100&type=1`

---

## Top Picks 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | add_top_picks | POST | `api/v2/top_picks/add_top_picks` | `add_top_picks.py` | [doc](https://open.shopee.com/documents/v2/v2.top_picks.add_top_picks?module=100&type=1) |
| 2 | delete_top_picks | POST | `api/v2/top_picks/delete_top_picks` | `delete_top_picks.py` | [doc](https://open.shopee.com/documents/v2/v2.top_picks.delete_top_picks?module=100&type=1) |
| 3 | get_top_picks_list | GET | `api/v2/top_picks/get_top_picks_list` | `get_top_picks_list.py` | [doc](https://open.shopee.com/documents/v2/v2.top_picks.get_top_picks_list?module=100&type=1) |
| 4 | update_top_picks | POST | `api/v2/top_picks/update_top_picks` | `update_top_picks.py` | [doc](https://open.shopee.com/documents/v2/v2.top_picks.update_top_picks?module=100&type=1) |
通用入口：`top_picks_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

| API | 要点 |
|-----|------|
| `get_top_picks_list` | 精选商品集合列表 |
| `add_top_picks` | 创建精选集合；POST `body` |
| `update_top_picks` | 更新精选集合 |
| `delete_top_picks` | 删除精选集合 |

---

## curl 示例

```bash
curl -X POST ${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/top_picks/get_top_picks_list",
    "method": "GET",
    "accessToken": "xxx",
    "shopId": "67890"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-top-picks","sentiment":"POSITIVE",
       "category":"OTHER","content":"Top Picks查询正常"}'
```
