# Shopee 精选商品 Top Picks 接口说明

本技能定义 4 项 Top Picks 转发操作及 1 项兼容店铺授权状态查询辅助操作；Feedback 不计入业务接口。网关均使用 POST，转发操作的上游方法由请求体 `method` 决定。

| 接口 | 文档 | 上游方法 / 转发 path |
|---|---|---|
| 获取精选集合列表（`get_top_picks_list`） | [apis/get-top-picks-list.md](apis/get-top-picks-list.md) | `GET` / `api/v2/top_picks/get_top_picks_list` |
| 创建精选集合（`add_top_picks`） | [apis/add-top-picks.md](apis/add-top-picks.md) | `POST` / `api/v2/top_picks/add_top_picks` |
| 更新精选集合（`update_top_picks`） | [apis/update-top-picks.md](apis/update-top-picks.md) | `POST` / `api/v2/top_picks/update_top_picks` |
| 删除精选集合（`delete_top_picks`） | [apis/delete-top-picks.md](apis/delete-top-picks.md) | `POST` / `api/v2/top_picks/delete_top_picks` |
| 查询店铺授权状态（兼容） | [apis/store-tokens.md](apis/store-tokens.md) | 不转发；`POST /shopee/storeTokens` |

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

## 运行约定

| 项目 | 约定 |
|---|---|
| 依赖 | `linkfox-shopee-store-auth` 负责授权与选店；`scripts/check_auth_dependency.py` 返回 0 表示已安装，返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。不会在本技能内实现授权。 |
| 网关地址兼容 | 优先 `LINKFOX_TOOL_GATEWAY`，其次 `SHOPEE_API_BASE_URL`，最后默认正式地址；保留两种 API Key 环境变量兼容。 |
| 会话请求头 | 保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空字符串。 |
| 缓存 | 本技能业务封装不启用响应缓存；所有业务调用 `call_api.run` 强制加入 `--no-cache`，不复用也不保存响应缓存；调用器可能创建空缓存目录，不代表缓存启用。 |
| 落盘 | 数据仅保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`；请求前检查当前目录及实际会话 data 目录是否可写；失败即报错，不发出请求，不回退到用户目录或临时目录。会话标识应为有效目录名。 |
| 输出 | 每次精选调用保存一份含加工字段的完整 JSON；不超过 8000 UTF-8 字节时全量输出，超过时显示摘要；`--inline` 强制全量输出并仍保存文件。 |
| 授权状态辅助查询 | `storeTokens` 返回授权状态，不返回原始令牌；兼容函数在内存中保留原响应，保存副本按敏感信息规则隐藏非数值状态字段，不输出到 stdout。正常精选 CLI 不调用该接口。 |
| 通用入口 | `python scripts/top_picks_api.py '<JSON>' [--inline] [--no-cache]`；JSON 顶层必须为对象，格式或类型错误时在请求前报错退出；通用入口必须含注册的 `api` 名称。四个独立入口 CLI 保持相同 JSON 与选项用法。 |
| GET 编码 | 非保留且非 null 的标量字段进入查询串；布尔值转小写字符串，字典/数组跳过。值使用百分号编码，无 `?` 前缀。列表规范化函数接受逗号字符串或数组，去空后最多 50 项；本模块 `LIST_QUERY_FIELDS` 为空，不对任何字段启用该处理，50 项限制不适用于本模块查询字段。 |
| POST 组装 | `body` 优先于 `requestBody`；字符串原样透传，其他 JSON 值紧凑序列化；两者缺失才读取注册表 `body_fields`。本模块各接口注册表未配置该列表，POST 必须显式传入 `body` 或 `requestBody`，不支持顶层业务字段自动组装。 |
| 保留字段 | `shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 不进入自动构造的查询串；选店控制字段不自动注入上游 body。显式 body 由调用者负责只放业务字段。 |
| 结果不确定 | 写入超时或失败不自动重放；先解释已知结果，按用户任务范围核查现有集合。写入后核查或用户要求刷新时可再次读取相同店铺。失败或空结果不自动换参数、连续翻页。 |

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-top-picks",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
