# Shopee 店铺分类管理 接口说明

7 个 Shop Category 操作经统一端点转发；另提供授权状态查询辅助接口。

| 接口 | 文档 |
|---|---|
| `add_shop_category` | [apis/add-shop-category.md](apis/add-shop-category.md) |
| `get_shop_category_list` | [apis/get-shop-category-list.md](apis/get-shop-category-list.md) |
| `delete_shop_category` | [apis/delete-shop-category.md](apis/delete-shop-category.md) |
| `update_shop_category` | [apis/update-shop-category.md](apis/update-shop-category.md) |
| `add_item_list` | [apis/add-item-list.md](apis/add-item-list.md) |
| `get_item_list` | [apis/get-item-list.md](apis/get-item-list.md) |
| `delete_item_list` | [apis/delete-item-list.md](apis/delete-item-list.md) |
| `storeTokens`（辅助兼容） | [apis/store-tokens.md](apis/store-tokens.md) |

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 脚本运行约定

| 参数 / 约定 | 类型 | 说明 |
|---|---|---|
| `api` | string | 仅通用入口需要，取接口清单中 7 个分类操作名之一；固定操作脚本无需此字段。 |
| `skipDepCheck` | boolean | 默认 false；只跳过本地安装检测，不绕过店铺授权。 |
| `--inline` | CLI flag | 强制全量打印，仍保存完整响应。 |
| `--no-cache` | CLI flag | 业务脚本无响应缓存；封装调用 `call_api.run` 始终携带此选项，不读取或保存响应缓存；公共调用器可能创建空缓存目录。 |
| 认证变量 | string | 优先 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`。 |
| 网关变量 | string | 优先 `LINKFOX_TOOL_GATEWAY`，其次兼容 `SHOPEE_API_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。 |
| 依赖检查 | exit code | 返回 0 表示找到认证技能；42 与 stderr 的 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-shopee-store-auth`。 |
| 数据保存 | path | 当前工作目录下 `linkfox/<日期>/<session>/data/`；文件名含技能名和操作标识，微秒时间戳避免同秒覆盖；请求前检查最终会话 data 目录是否可写；不可写时报错，不回退到家目录或临时目录。 |
| 输出大小 | integer | 按 UTF-8 字节数，≤ 8000 全量输出，超过时仅摘要及最大列表前 3 条；`--inline` 覆盖此展示限制。 |

分类脚本格式：`python scripts/<操作名>.py '<JSON 参数>' [--inline] [--no-cache]`；通用入口为 `python scripts/shop_category_api.py '<含 api 的 JSON 参数>' [--inline] [--no-cache]`。
脚本保留完整网关响应，业务加工后由公共调用器保存一次，不引入第二层响应缓存。依赖检查支持各平台安装目录和环境变量搜索。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-shop-category",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
