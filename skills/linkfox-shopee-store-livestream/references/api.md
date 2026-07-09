# linkfox-shopee-store-livestream — 参数与字段参考

Shopee **Livestream 模块**全部 25 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.livestream.upload_image](https://open.shopee.com/documents/v2/v2.livestream.upload_image?module=125&type=1)

## 通用约定

- **path**：须 `api/v2/livestream/...`
- **标识**：通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.livestream.{api}?module=125&type=1`

---

## Livestream 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | add_item_list | POST | `api/v2/livestream/add_item_list` | `add_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.add_item_list?module=125&type=1) |
| 2 | apply_item_set | POST | `api/v2/livestream/apply_item_set` | `apply_item_set.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.apply_item_set?module=125&type=1) |
| 3 | ban_user_comment | POST | `api/v2/livestream/ban_user_comment` | `ban_user_comment.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.ban_user_comment?module=125&type=1) |
| 4 | create_session | POST | `api/v2/livestream/create_session` | `create_session.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.create_session?module=125&type=1) |
| 5 | delete_item_list | POST | `api/v2/livestream/delete_item_list` | `delete_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.delete_item_list?module=125&type=1) |
| 6 | delete_show_item | POST | `api/v2/livestream/delete_show_item` | `delete_show_item.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.delete_show_item?module=125&type=1) |
| 7 | end_session | POST | `api/v2/livestream/end_session` | `end_session.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.end_session?module=125&type=1) |
| 8 | get_item_count | GET | `api/v2/livestream/get_item_count` | `get_item_count.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.get_item_count?module=125&type=1) |
| 9 | get_item_list | GET | `api/v2/livestream/get_item_list` | `get_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.get_item_list?module=125&type=1) |
| 10 | get_item_set_item_list | GET | `api/v2/livestream/get_item_set_item_list` | `get_item_set_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.get_item_set_item_list?module=125&type=1) |
| 11 | get_item_set_list | GET | `api/v2/livestream/get_item_set_list` | `get_item_set_list.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.get_item_set_list?module=125&type=1) |
| 12 | get_latest_comment_list | GET | `api/v2/livestream/get_latest_comment_list` | `get_latest_comment_list.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.get_latest_comment_list?module=125&type=1) |
| 13 | get_like_item_list | GET | `api/v2/livestream/get_like_item_list` | `get_like_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.get_like_item_list?module=125&type=1) |
| 14 | get_recent_item_list | GET | `api/v2/livestream/get_recent_item_list` | `get_recent_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.get_recent_item_list?module=125&type=1) |
| 15 | get_session_detail | GET | `api/v2/livestream/get_session_detail` | `get_session_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.get_session_detail?module=125&type=1) |
| 16 | get_session_item_metric | GET | `api/v2/livestream/get_session_item_metric` | `get_session_item_metric.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.get_session_item_metric?module=125&type=1) |
| 17 | get_session_metric | GET | `api/v2/livestream/get_session_metric` | `get_session_metric.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.get_session_metric?module=125&type=1) |
| 18 | get_show_item | GET | `api/v2/livestream/get_show_item` | `get_show_item.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.get_show_item?module=125&type=1) |
| 19 | post_comment | POST | `api/v2/livestream/post_comment` | `post_comment.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.post_comment?module=125&type=1) |
| 20 | start_session | POST | `api/v2/livestream/start_session` | `start_session.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.start_session?module=125&type=1) |
| 21 | unban_user_comment | POST | `api/v2/livestream/unban_user_comment` | `unban_user_comment.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.unban_user_comment?module=125&type=1) |
| 22 | update_item_list | POST | `api/v2/livestream/update_item_list` | `update_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.update_item_list?module=125&type=1) |
| 23 | update_session | POST | `api/v2/livestream/update_session` | `update_session.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.update_session?module=125&type=1) |
| 24 | update_show_item | POST | `api/v2/livestream/update_show_item` | `update_show_item.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.update_show_item?module=125&type=1) |
| 25 | upload_image | POST | `api/v2/livestream/upload_image` | `upload_image.py` | [doc](https://open.shopee.com/documents/v2/v2.livestream.upload_image?module=125&type=1) |
通用入口：`livestream_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

| 分类 | API | 要点 |
|------|-----|------|
| 会话 | `create_session` / `start_session` / `end_session` | 创建、开始、结束直播 |
| 会话 | `get_session_detail` / `get_session_metric` | 场次详情与数据 |
| 商品 | `add_item_list` / `get_item_list` / `update_show_item` | 直播商品管理 |
| 商品集 | `get_item_set_list` / `apply_item_set` | 商品集应用 |
| 互动 | `get_latest_comment_list` / `post_comment` | 评论管理 |
| 互动 | `ban_user_comment` / `unban_user_comment` | 禁言管理 |
| 素材 | `upload_image` | 上传直播图片 |

---

## curl 示例

```bash
curl -X POST ${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy \
  -H "Authorization: $LINKFOX_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/livestream/get_session_detail",
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
  -d '{"skillName":"linkfox-shopee-store-livestream","sentiment":"POSITIVE",
       "category":"OTHER","content":"直播接口查询正常"}'
```
