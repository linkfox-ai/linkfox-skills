# linkfox-shopee-store-push — 参数与字段参考

Shopee **Push 模块**全部 4 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.push.set_app_push_config](https://open.shopee.com/documents/v2/v2.push.set_app_push_config?module=105&type=1)

## 通用约定

- **path**：须 `api/v2/push/...`
- **Partner 级接口**：Push 配置与补推通常为 Partner/App 级，通常无需 `shopId`
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.push.{api}?module=105&type=1`

---

## Push 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | confirm_consumed_lost_push_message | POST | `api/v2/push/confirm_consumed_lost_push_message` | `confirm_consumed_lost_push_message.py` | [doc](https://open.shopee.com/documents/v2/v2.push.confirm_consumed_lost_push_message?module=105&type=1) |
| 2 | get_app_push_config | GET | `api/v2/push/get_app_push_config` | `get_app_push_config.py` | [doc](https://open.shopee.com/documents/v2/v2.push.get_app_push_config?module=105&type=1) |
| 3 | get_lost_push_message | GET | `api/v2/push/get_lost_push_message` | `get_lost_push_message.py` | [doc](https://open.shopee.com/documents/v2/v2.push.get_lost_push_message?module=105&type=1) |
| 4 | set_app_push_config | POST | `api/v2/push/set_app_push_config` | `set_app_push_config.py` | [doc](https://open.shopee.com/documents/v2/v2.push.set_app_push_config?module=105&type=1) |
通用入口：`push_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

| API | 要点 |
|-----|------|
| `set_app_push_config` | 配置 Push 回调 URL 与推送设置；POST `body` |
| `get_app_push_config` | 查询当前 Push 配置 |
| `get_lost_push_message` | 获取丢失的 Push 消息（补推） |
| `confirm_consumed_lost_push_message` | 确认已消费补推消息；POST `body` |

---

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/shopee/developerProxy \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/push/get_app_push_config",
    "method": "GET",
    "accessToken": "xxx"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-push","sentiment":"POSITIVE",
       "category":"OTHER","content":"Push配置查询正常"}'
```
