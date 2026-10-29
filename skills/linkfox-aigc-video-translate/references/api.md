# 视频翻译 API 参考

## 调用规范

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/aigc/videoTranslation`，网关未配置时回退正式网关。
- POST JSON；Authorization 优先读取 LINKFOX_AGENT_API_KEY，回退 LINKFOXAGENT_API_KEY；禁止在参数或落盘文件中存储凭证。
- Content-Type: application/json；User-Agent: LinkFox-Skill/2.0；HTTP超时150s。
- 透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 环境变量。
- 网关契约以tools的feature-workbuddy-change分支为准：外层OpenApiImageMakeDto、params内业务参数参考下载文档。实际下游为Agent专用入口，不能把版本化OpenAPI路径当成网关路径。

## 所有素材前置上传

本地图片／视频必须先执行 [file-upload.md](file-upload.md) 中的 本目录内置Base64上传 流程，取得 viewUrl 后填入下表的媒体字段。外部公开 URL 也必须先下载并调用上传接口，生成字段只使用返回的 viewUrl。上传失败停止，不提交生成任务；查询不重复上传。

## 完整执行与交付

推荐 `scripts/run_task.py` 完成素材上传、创建、taskQuery轮询和媒体下载。params内的媒体字段在该辅助入口中允许本地路径或外部 URL；真正发给生成 API 前统一转换为 uploadByBase64 返回的 viewUrl。原官方创建脚本不承担上传或轮询，不能直接给它外部源 URL。

支持 JSON 参数、`--params-file <参数文件>` 或 `-` 从 stdin 读取；requestId 仅在入参提供时原样转发，缺失时不自动生成。超时后使用 `--task-id <已接受任务ID>` 继续查询，不再次上传或创建。恢复只接受 taskId 和可选 memberId，不能混入创建参数。

终态query JSON保留实际费用与任务级错误；当前后端不透出单项生成错误。成功文件下载到 `<session>/media/`，资产清单写入 `<session>/data/`；清单提供 localPath、下载失败项和费用。stdout 的 `Saved full response: [本地路径数组]` 用于前端媒体展示，不要原样复述给用户。下载失败可用 `scripts/download_results.py <终态查询JSON>` 重试，不产生新生成任务。

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| requestId | String | 否 | 可选兼容字段；提供时原样转发，缺失时不补充 |
| chatId | String | 否 | 旧Agent会话ID，最长128字符 |
| messageId | String | 否 | 旧Agent消息ID，最长128字符 |
| title | String | 否 | 业务展示标题 |
| params | Object | 是 | 非空业务参数对象，字段见下表；身份由认证凭证解析，不传顶层memberId |

## params业务参数

以下必填及模型限制来自业务文档；本分支本地只校验params非空，具体业务校验由下游执行。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.sourceVideoUrl | String | 是 | 待翻译原视频的公网 URL；服务端会读取真实媒体时长用于计费|
| params.targetLanguage | String | 是 | 目标语言，支持短代码或 BCP-47 代码，详见下方语言表|
| params.sourceVideoName | String | 否或条件必填 | 原视频文件名，仅用于历史记录展示|
| params.lipSync | Boolean | 否或条件必填 | 是否同步口型；默认 true |
| params.videoType | String | 否或条件必填 | 视频翻译模型；不传时使用默认模型，支持值见下方扣费标准|

## 公共任务上下文

请求外层只定义requestId、chatId、messageId、title、params。业务参数必须放params；成员和团队由服务端根据认证身份解析，不能靠memberId字段指定。chatId/messageId最长128字符。普通skill不发送渠道头时externalAgentPlatform默认skill；不要自行伪装workbuddy。

本分支实际下游创建路径：`/image/auth/agent/imagemake/videoTranslation`。下方V3/V4文档仅说明params业务能力，不能据此更换实际调用路径。

## 响应与查询

创建返回taskId及costToken=0，0不代表免费。使用本目录scripts/query_task.py调用 `/aigc/taskQuery`，请求taskId及可选memberId，每次使用--no-cache。该查询也服务原有图像/视频任务，不存在本分支专属的makeTaskQuery接口。

查询响应字段：taskId、status（PROCESSING/SUCCESS/FAILED）、resultList、errorMsg、costToken。结果项仅定义id、url、type；type取自下游extendField.type。当前后端不返回单项status/errorCode/errorMsg、width/height/format/size、完整extendField或containsSyntheticPerformer；skill不得推断未返回的信息，也不能通过查询传format或containsSyntheticPerformer。

费用仍由下游处理，count按2000倍换算。官方脚本保留响应头X-Cost-Token/X-Cost-Credit提供的实际费用，不使用创建时的0覆盖查询费用。没有费用时表示未知。

## 素材准备

本地图片或视频读取并按内置 [file-upload.md](file-upload.md)执行上传。外部URL也必须先下载上传，生成接口只使用上传返回的viewUrl。仅处理本次接口实际需要的素材：视频翻译不要求额外上传图片，视频编辑的参考图片可选。

## 下游业务字段及模型参考

以下为已下载的业务文档，仅作为字段、模型限制及业务条件参考。其中下游id/status/count/响应封装不能替代上方网关taskId/status/costToken契约；文档里的单项扩展字段当前未由网关结果VO透出。

# 视频翻译 V3

识别原视频语音并翻译为目标语言，生成翻译后的视频；口型同步默认开启。

**下游 POST** `/image/v3/make/videoTranslation`  
Content-Type: `application/json`

---

### 请求体

| 参数 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| sourceVideoUrl | string | 必填 | 待翻译原视频的公网 URL；服务端会读取真实媒体时长用于计费 |
| targetLanguage | string | 必填 | 目标语言，支持短代码或 BCP-47 代码，详见下方语言表 |
| sourceVideoName | string | 可选 | 原视频文件名，仅用于历史记录展示 |
| lipSync | boolean | 可选 | 是否同步口型；默认 true |
| videoType | string | 可选 | 视频翻译模型；不传时使用默认模型，支持值见下方[扣费标准](#扣费标准) |

---

### 支持的语言

`targetLanguage` 必须使用下表中的语言。源语言由服务端自动识别，不提供源语言请求参数。

| 语言 | 短代码 | BCP-47 代码 |
| --- | --- | --- |
| 中文 | `zh` | `zh-CN` |
| 英语 | `en` | `en-US` |
| 日语 | `ja` | `ja-JP` |
| 韩语 | `ko` | `ko-KR` |
| 西班牙语 | `es` | `es-ES` |
| 法语 | `fr` | `fr-FR` |
| 德语 | `de` | `de-DE` |
| 葡萄牙语 | `pt` | `pt-BR` |
| 阿拉伯语 | `ar` | `ar-SA` |
| 泰语 | `th` | `th-TH` |
| 越南语 | `vi` | `vi-VN` |
| 印尼语 | `id` | `id-ID` |
| 马来语 | `ms` | `ms-MY` |

目标语言代码匹配不区分大小写，并兼容下划线形式（例如 `en_US`）。

---

### 模型与生成规则

自动识别原视频语言，按 `targetLanguage` 翻译；`lipSync` 控制是否同步口型。不传 `videoType` 时使用默认模型；可灵模型也跟随原视频时长。

---

### 时长规则

所有模型均跟随原视频时长，不支持自定义时长，无需传 `videoTime` 或 `duration`。请使用可持续访问的视频 URL；计费时长按原视频实际时长向下取整为整数秒，具体扣费见页面末尾。

---

### 请求示例

**默认模型**

自动识别原视频语音，翻译为英语并同步口型

```json
{
  "sourceVideoUrl": "https://example.com/source.mp4",
  "targetLanguage": "en"
}
```

**doubao-seedance-2-5**

指定模型，关闭口型同步

```json
{
  "sourceVideoUrl": "https://example.com/source-ko.mp4",
  "targetLanguage": "zh-CN",
  "lipSync": false,
  "videoType": "doubao-seedance-2-5"
}
```

---

### 提交后返回什么

提交成功后返回任务编号 `data.id`，表示任务已创建，结果还需等待生成。请保存编号。查看返回示例（辅助接口不在本skill范围）。

### 查询生成结果

用任务编号 `data.id` 调用获取作图结果（辅助接口不在本skill范围），每次查询至少间隔 10 秒。`data.status=3` 表示成功；若生成了图片或视频，从 `data.resultList[].url` 获取地址。`data.status=4` 表示失败。查看统一示例（辅助接口不在本skill范围）。

### 常见问题

- **目标语言无效**：确认使用支持语言表中的短代码或 BCP-47 代码。
- **模型不可用**：不传 `videoType` 使用默认模型，或确认传入值是「扣费标准」中展示的公开模型名称。
- **无法读取原视频时长**：确认 URL 可公网访问、未过期，并且返回可解析的视频内容。
- **任务失败或长时间无结果**：确认视频地址在异步任务执行期间持续可访问，并检查内容合规、账户算力和上游模型状态。

### 扣费标准

以下扣点从当前模型配置实时读取。

| 模型 | 扣费配置（点/秒） |
| --- | --- |
| happyhorse-v2 | 按时长：**39** |
| doubao-seedance-2-5 （配置默认） | 按时长：支持有声 **71** |

> 扣点数 = 单价（点/秒）× 计费时长（秒）。计费时长按原视频实际时长向下取整为整数秒；如果当前模型设置了计费时长上限，则以该上限为准。


## curl示例

```bash
curl "${LINKFOX_TOOL_GATEWAY}/aigc/videoTranslation" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H 'Content-Type: application/json' -H 'User-Agent: LinkFox-Skill/2.0' \
  --data '{"params": {"sourceVideoUrl": "https://example.com/source.mp4", "targetLanguage": "en", "lipSync": true}}'
```

以上参数仅为结构示例；必须替换为真实素材和模型，不能调用示例占位地址执行收费测试。

## 错误处理

HTTP200不保证业务成功。检查error、errcode及code；无成功字段时不要继续依赖链。处理400参数错误、401/403认证或归属失败、402余额不足、404任务不存在及下游错误。模板支持网关ToolErrorResponse XML标准化。不要只依赖脚本退出码，失败响应可能仍被保存为JSON。

未配置Key、401鉴权异常或402余额不足时，读取本skill内置 [onboarding.md](onboarding.md)，按原有AIGC流程引导。403成员归属或权限失败不能通过充值解决。手机号登录、短信及套餐支付按用户选择执行，不自动操作；不将登录Token、验证码或Key写入任务产物。

## Feedback

反馈接口：https://skill-api.linkfox.com/api/v1/public/feedback 。记录路径、requestId/taskId及脱敏错误摘要；参数类型不符、异常响应结构、持续查询失败可反馈。绝不包含Key、Authorization、Base64或私密素材内容。
