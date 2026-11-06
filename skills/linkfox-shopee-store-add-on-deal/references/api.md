# Shopee 加购优惠 Add-On Deal 接口说明

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

## 接口索引

本技能定义 14 个 Add-On Deal 操作，经 `POST /shopee/developerProxy` 转发。每个接口文档独立列出转发方法、完整已定义字段和响应规则；不包含授权技能的接口操作。

| 接口 | 说明 | 接口文档 |
|---|---|---|
| `add_add_on_deal` | 创建加购优惠 | [add-add-on-deal.md](apis/add-add-on-deal.md) |
| `add_add_on_deal_main_item` | 添加主商品 | [add-add-on-deal-main-item.md](apis/add-add-on-deal-main-item.md) |
| `add_add_on_deal_sub_item` | 添加加购商品 | [add-add-on-deal-sub-item.md](apis/add-add-on-deal-sub-item.md) |
| `delete_add_on_deal` | 删除加购优惠 | [delete-add-on-deal.md](apis/delete-add-on-deal.md) |
| `delete_add_on_deal_main_item` | 删除主商品 | [delete-add-on-deal-main-item.md](apis/delete-add-on-deal-main-item.md) |
| `delete_add_on_deal_sub_item` | 删除加购商品 | [delete-add-on-deal-sub-item.md](apis/delete-add-on-deal-sub-item.md) |
| `get_add_on_deal_list` | 查询加购优惠列表 | [get-add-on-deal-list.md](apis/get-add-on-deal-list.md) |
| `get_add_on_deal` | 查询加购优惠详情 | [get-add-on-deal.md](apis/get-add-on-deal.md) |
| `get_add_on_deal_main_item` | 查询主商品列表 | [get-add-on-deal-main-item.md](apis/get-add-on-deal-main-item.md) |
| `get_add_on_deal_sub_item` | 查询加购商品列表 | [get-add-on-deal-sub-item.md](apis/get-add-on-deal-sub-item.md) |
| `update_add_on_deal` | 更新加购优惠 | [update-add-on-deal.md](apis/update-add-on-deal.md) |
| `update_add_on_deal_main_item` | 更新主商品设置 | [update-add-on-deal-main-item.md](apis/update-add-on-deal-main-item.md) |
| `update_add_on_deal_sub_item` | 更新加购商品设置 | [update-add-on-deal-sub-item.md](apis/update-add-on-deal-sub-item.md) |
| `end_add_on_deal` | 提前结束加购优惠 | [end-add-on-deal.md](apis/end-add-on-deal.md) |

## 脚本运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| api | string | 仅通用入口必填 | `scripts/add_on_deal_api.py` 用此字段选择上述 14 个操作；独立脚本已固定操作。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖安装检查，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制全量打印，完整响应仍保存。 |
| --no-cache | CLI flag | 否 | 所有业务入口始终向 `call_api.run` 加入此选项，不读取或写入响应缓存；可显式传入以兼容公共 CLI。 |

本地依赖检查返回 0 表示找到 `linkfox-shopee-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装依赖。检测覆盖环境变量指定路径、工作区和常见安装目录；不能在本技能中绕过依赖实现授权。

`LINKFOX_TOOL_GATEWAY` 优先，其次兼容 `SHOPEE_API_BASE_URL`，最后为默认网关地址。密钥兼容公共规则中的两个环境变量。传输保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。

业务脚本保存完整响应到当前工作目录的 `linkfox/<YYYY-MM-DD>/<session>/data/`；每个文件名包含本技能及操作标识，重复调用也独立保存。请求前检查根目录及实际日期、会话和 data 目录；目录被同名文件阻塞或不可写时立即报错，不提交店铺操作，也不回退到家目录或临时目录。会话优先使用 `SESSION_ID`，同时维护 `_meta.json` 和 `index.jsonl`。公共调用器可能创建空 `.cache` 目录，但不产生或复用响应缓存文件。

通用入口和 14 个独立入口均接受 JSON 参数及 `--inline` / `--no-cache`；默认输出阈值为 8000 UTF-8 字节，大响应只展示摘要，完整内容在保存文件中。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-add-on-deal",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
