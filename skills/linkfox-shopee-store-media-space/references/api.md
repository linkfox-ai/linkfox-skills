# Shopee 媒体 MediaSpace 接口说明

共六个媒体操作及一个店铺授权状态辅助操作（不含 Feedback 与公共认证引导）。当前媒体流程由服务端按店铺解析 token，不调用 storeTokens；辅助操作也不返回原始令牌。按操作读取下列独立文档。

- [初始化视频上传（init_video_upload）](apis/init-video-upload.md)
- [上传视频分片（upload_video_part）](apis/upload-video-part.md)
- [完成视频上传（complete_video_upload）](apis/complete-video-upload.md)
- [查询视频上传结果（get_video_upload_result）](apis/get-video-upload-result.md)
- [取消视频上传（cancel_video_upload）](apis/cancel-video-upload.md)
- [上传图片（upload_image）](apis/upload-image.md)
- [店铺授权状态辅助函数（storeTokens）](apis/store-tokens.md)

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

| 项目 | 约定 |
|------|------|
| 店铺依赖 | 先执行 `python scripts/check_auth_dependency.py`；返回 0 且 stderr 含 `DEPENDENCY_OK:` 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装 `linkfox-shopee-store-auth`。各媒体入口默认执行同一检查。 |
| 依赖搜索 | 支持 LINKFOX_SKILLS_DIR、SKILLS_DIR、CURSOR_SKILLS_DIR、HERMES_SKILLS_EXTERNAL_DIRS、OPENCLAW_WORKSPACE / ROOT / WORKDIR、OPENCLAW_SKILLS_DIR、当前项目、相邻技能及用户常见安装目录探测。 |
| 认证兼容 | `LINKFOX_AGENT_API_KEY` 优先，其次 `LINKFOXAGENT_API_KEY`；网关 `LINKFOX_TOOL_GATEWAY` 优先，其次兼容变量 `SHOPEE_API_BASE_URL`，最后正式地址。保留会话追踪头 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。 |
| 通用入口 | `python scripts/media_space_api.py '<JSON 参数>' [--inline] [--no-cache]`；JSON 的 api 字段仅接受六个媒体操作名称。专用脚本使用同样参数但无需 api。 |
| 缓存 | 业务封装调用 `call_api.run` 始终传 `--no-cache`；不会读写响应缓存。公共调用器可能创建空 `.cache` 目录，不代表缓存响应。 |
| 会话落盘 | 网关原始响应与业务加工结果均保存在当前工作目录的 linkfox/日期/会话/data/；业务结果文件使用技能名、接口标识和微秒时间戳，原始响应另带 gateway 标识。禁止回退到用户目录或临时目录；请求前创建实际会话数据目录并验证原始响应目标文件可写；不可写时直接报错。 |
| 输出 | 不超过 8000 字节打印完整 JSON；更大时展示摘要；--inline 强制全量打印。完整结果始终落盘。 |
| 视频上游契约 | 视频接口使用透传的上游请求，本文不列出完整的上游字段、必填项、枚举或默认值；不得从示例推断完整 schema。按实际素材及 Shopee 官方规范准备 body/query，缺少必需信息先补齐。 |

## 网关业务错误

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 400（HTTP 400） | path、method 或图片参数等不合法 | 按 errmsg 修正参数；不自动换参试探。 |
| 503（HTTP 503） | 代理或图片上传的上游网络异常 | 保留实际 HTTP 状态与 errmsg；说明原因后按任务范围决定是否重试。 |
| 1002 | 参数或未登录 | 核对店铺标识与 API Key。 |
| 1003 | 服务端刷新授权失败等代理依赖异常 | 按 errmsg 解释；后续重试遵守调用约束，不连续试探。 |
| 1004 | 无授权记录 | 交给认证技能核对店铺授权。 |
| 1005 | path 未在白名单 | 核对 MediaSpace 相对路径及后端放行配置。 |

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-media-space",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
