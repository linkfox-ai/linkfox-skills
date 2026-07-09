# linkfox-shopee-store-follow-prize — 参数与字段参考

Shopee **Follow Prize 模块**全部 6 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.follow_prize.add_follow_prize](https://open.shopee.com/documents/v2/v2.follow_prize.add_follow_prize?module=113&type=1)

## 通用约定

- **path**：须 `api/v2/follow_prize/...`
- **标识**：通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.follow_prize.{api}?module=113&type=1`

---

## Follow Prize 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | add_follow_prize | POST | `api/v2/follow_prize/add_follow_prize` | `add_follow_prize.py` | [doc](https://open.shopee.com/documents/v2/v2.follow_prize.add_follow_prize?module=113&type=1) |
| 2 | delete_follow_prize | POST | `api/v2/follow_prize/delete_follow_prize` | `delete_follow_prize.py` | [doc](https://open.shopee.com/documents/v2/v2.follow_prize.delete_follow_prize?module=113&type=1) |
| 3 | end_follow_prize | POST | `api/v2/follow_prize/end_follow_prize` | `end_follow_prize.py` | [doc](https://open.shopee.com/documents/v2/v2.follow_prize.end_follow_prize?module=113&type=1) |
| 4 | get_follow_prize_detail | GET | `api/v2/follow_prize/get_follow_prize_detail` | `get_follow_prize_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.follow_prize.get_follow_prize_detail?module=113&type=1) |
| 5 | get_follow_prize_list | GET | `api/v2/follow_prize/get_follow_prize_list` | `get_follow_prize_list.py` | [doc](https://open.shopee.com/documents/v2/v2.follow_prize.get_follow_prize_list?module=113&type=1) |
| 6 | update_follow_prize | POST | `api/v2/follow_prize/update_follow_prize` | `update_follow_prize.py` | [doc](https://open.shopee.com/documents/v2/v2.follow_prize.update_follow_prize?module=113&type=1) |
通用入口：`follow_prize_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

| API | 要点 |
|-----|------|
| `add_follow_prize` | 创建关注有礼活动；POST `body` |
| `get_follow_prize_list` | 活动列表 |
| `get_follow_prize_detail` | 活动详情 |
| `update_follow_prize` | 更新活动 |
| `end_follow_prize` | 提前结束 |
| `delete_follow_prize` | 删除活动 |

---

## curl 示例

```bash
curl -X POST ${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy \
  -H "Authorization: $LINKFOX_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/follow_prize/get_follow_prize_list",
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
  -d '{"skillName":"linkfox-shopee-store-follow-prize","sentiment":"POSITIVE",
       "category":"OTHER","content":"关注有礼查询正常"}'
```
