# 视频编辑 API 参考

## 调用规范

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/aigc/videoEditing`，网关未配置时回退正式网关。
- POST JSON；Authorization 优先读取 LINKFOX_AGENT_API_KEY，回退 LINKFOXAGENT_API_KEY；禁止在参数或落盘文件中存储凭证。
- Content-Type: application/json；User-Agent: LinkFox-Skill/2.0；HTTP超时150s。
- 透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 环境变量。
- 网关契约以tools的feature-workbuddy-change分支为准：外层OpenApiImageMakeDto、params内业务参数参考下载文档。实际下游为Agent专用入口，不能把版本化OpenAPI路径当成网关路径。

## 所有素材前置上传

本地图片／视频必须先执行 [file-upload.md](file-upload.md) 中的 本目录内置Base64上传 流程，取得 viewUrl 后填入下表的媒体字段。外部公开 URL 也必须先下载并调用上传接口，生成字段只使用返回的 viewUrl。上传失败停止，不提交生成任务；查询不重复上传。

## 完整执行与交付

推荐 `scripts/run_task.py` 完成素材上传、创建、taskQuery轮询和媒体下载。params内的媒体字段在该辅助入口中允许本地路径或外部 URL；真正发给生成 API 前统一转换为 uploadByBase64 返回的 viewUrl。原官方创建脚本不承担上传或轮询，不能直接给它外部源 URL。

支持 JSON 参数、`--params-file <参数文件>` 或 `-` 从 stdin 读取；缺失 requestId 时生成新的唯一 ID。超时后使用 `--task-id <已接受任务ID>` 继续查询，不再次上传或创建。恢复只接受 taskId 和可选 memberId，不能混入创建参数。

终态query JSON保留实际费用与任务级错误；当前后端不透出单项生成错误。成功文件下载到 `<session>/media/`，资产清单写入 `<session>/data/`；清单提供 localPath、下载失败项和费用。stdout 的 `Saved full response: [本地路径数组]` 用于前端媒体展示，不要原样复述给用户。下载失败可用 `scripts/download_results.py <终态查询JSON>` 重试，不产生新生成任务。

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| requestId | String | 否 | 稳定业务请求ID；新任务使用唯一值，同一任务不得自动重复创建 |
| chatId | String | 否 | 旧Agent会话ID，最长128字符 |
| messageId | String | 否 | 旧Agent消息ID，最长128字符 |
| title | String | 否 | 业务展示标题 |
| params | Object | 是 | 非空业务参数对象，字段见下表；身份由认证凭证解析，不传顶层memberId |

## params业务参数

以下必填及模型限制来自业务文档；本分支本地只校验params非空，具体业务校验由下游执行。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.sourceVideoUrl | String | 是 | 待编辑原视频的公网 URL；跟随原视频模型会由服务端读取真实媒体时长用于执行与计费|
| params.prompt | String | 是 | 视频编辑指令，最多 2500 字符|
| params.videoType | String | 是 | 选择下方模型参数中的公开模型名称|
| params.videoTime | Integer | 否或条件必填 | 输出时长（秒），见下方时长规则；固定时长模型未传时使用当前模型默认值 |
| params.refImageList | List<String> | 否或条件必填 | 参考图片 URL 列表，数量上限见下方模型参数|

## 公共任务上下文

请求外层只定义requestId、chatId、messageId、title、params。业务参数必须放params；成员和团队由服务端根据认证身份解析，不能靠memberId字段指定。chatId/messageId最长128字符。普通skill不发送渠道头时externalAgentPlatform默认skill；不要自行伪装workbuddy。

本分支实际下游创建路径：`/image/auth/agent/imagemake/videoEditing`。下方V3/V4文档仅说明params业务能力，不能据此更换实际调用路径。

## 响应与查询

创建返回taskId及costToken=0，0不代表免费。使用本目录scripts/query_task.py调用 `/aigc/taskQuery`，请求taskId及可选memberId，每次使用--no-cache。该查询也服务原有图像/视频任务，不存在本分支专属的makeTaskQuery接口。

查询响应字段：taskId、status（PROCESSING/SUCCESS/FAILED）、resultList、errorMsg、costToken。结果项仅定义id、url、type；type取自下游extendField.type。当前后端不返回单项status/errorCode/errorMsg、width/height/format/size、完整extendField或containsSyntheticPerformer；skill不得推断未返回的信息，也不能通过查询传format或containsSyntheticPerformer。

费用仍由下游处理，count按2000倍换算。官方脚本保留响应头X-Cost-Token/X-Cost-Credit提供的实际费用，不使用创建时的0覆盖查询费用。没有费用时表示未知。

## 素材准备

本地图片或视频读取并按内置 [file-upload.md](file-upload.md)执行上传。外部URL也必须先下载上传，生成接口只使用上传返回的viewUrl。仅处理本次接口实际需要的素材：视频翻译不要求额外上传图片，视频编辑的参考图片可选。

## 下游业务字段及模型参考

以下为已下载的业务文档，仅作为字段、模型限制及业务条件参考。其中下游id/status/count/响应封装不能替代上方网关taskId/status/costToken契约；文档里的单项扩展字段当前未由网关结果VO透出。

# 视频编辑 V3

根据原视频、编辑指令和可选参考图片生成编辑后的视频，适用于背景替换、主体保持、风格调整等场景。

**下游 POST** `/image/v3/make/videoEditing`  
Content-Type: `application/json`

---

### 请求体

| 参数 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| sourceVideoUrl | string | 必填 | 待编辑原视频的公网 URL；跟随原视频模型会由服务端读取真实媒体时长用于执行与计费 |
| prompt | string | 必填 | 视频编辑指令，最多 2500 字符 |
| videoType | string | 必填 | 选择下方[模型参数](#模型参数)中的公开模型名称 |
| videoTime | integer | 可选 | 输出时长（秒），见下方[时长规则](#时长规则)；固定时长模型未传时使用当前模型默认值 |
| refImageList | array[string] | 可选 | 参考图片 URL 列表，数量上限见下方[模型参数](#模型参数) |

---

### 模型参数

`videoType` 请使用下表中的公开模型名称；模型是否可用以接口实际返回为准。

| videoType | 模型名称 | videoTime 允许值 | refImageList 上限 |
| --- | --- | --- | --- |
| `kling-v3-omni` | 可灵 V3-Omni | `-1` | 4 张 |
| `gemini-omni-flash` | Gemini Omni Flash 1.1 | `-1` | 10 张 |
| `doubao-seedance-2-0` | 豆包 Seedance 2.0 | 5 / 10 / 15 | 6 张 |
| `happyhorse-v2` | HappyHorse | `-1` | 9 张 |
| `WAN3` | 万相 3.0 | 5 / 10 / 15 | 10 张 |
| `doubao-seedance-2-5` | 豆包 Seedance 2.5 | `-1` | 30 张 |

---

### 时长规则

#### 跟随原视频时长

`videoTime=-1` 表示输出时长跟随原视频。以下模型只支持该模式：

- `kling-v3-omni`
- `gemini-omni-flash`
- `happyhorse-v2`
- `doubao-seedance-2-5`

> `happy-horse-v2` 是兼容别名，新接入请使用 `happyhorse-v2`。

- 系统会读取原视频的真实时长；视频无法访问或无法识别时长时，任务不会创建。
- 上述模型不要传 5、10、15 等固定时长，否则会返回参数错误。

#### 固定时长可选

- `doubao-seedance-2-0` 和 `WAN3` 支持 5 / 10 / 15 秒。
- 不传 `videoTime` 时使用当前模型默认时长；这两类模型不支持 `-1`。

#### 原视频时长限制

- 固定输出时长不等于原视频时长上限；可处理的原视频长度以模型实际能力为准。
- 建议使用稳定可访问的 HTTPS 视频地址，并控制原视频长度，避免任务在生成阶段失败。

---

### 请求示例

**doubao-seedance-2-5**

Seedance 2.5，跟随原视频时长

```json
{
  "sourceVideoUrl": "https://example.com/source.mp4",
  "prompt": "保持人物动作和镜头节奏不变，将背景替换为海滩",
  "videoType": "doubao-seedance-2-5",
  "refImageList": [
    "https://example.com/reference.png"
  ]
}
```

**WAN3**

WAN3，固定 10 秒

```json
{
  "sourceVideoUrl": "https://example.com/source.mp4",
  "prompt": "保留商品主体，将场景调整为明亮的现代客厅",
  "videoType": "WAN3",
  "videoTime": 10,
  "refImageList": [
    "https://example.com/product-main.jpg",
    "https://example.com/product-detail.jpg"
  ]
}
```

**kling-v3-omni**

可灵 V3-Omni，跟随原视频时长

```json
{
  "sourceVideoUrl": "https://example.com/source.mp4",
  "prompt": "保持主体和构图不变，将整体风格调整为电影质感",
  "videoType": "kling-v3-omni",
  "videoTime": -1
}
```

**doubao-seedance-2-0**

Seedance 2.0，不传时长使用模型默认固定时长

```json
{
  "sourceVideoUrl": "https://example.com/source.mp4",
  "prompt": "保持人物身份和动作一致，将服装颜色改为深蓝色",
  "videoType": "doubao-seedance-2-0"
}
```

---

### 提交后返回什么

提交成功后返回任务编号 `data.id`，表示任务已创建，结果还需等待生成。请保存编号。查看返回示例（辅助接口不在本skill范围）。

### 查询生成结果

用任务编号 `data.id` 调用获取作图结果（辅助接口不在本skill范围），每次查询至少间隔 10 秒。`data.status=3` 表示成功；若生成了图片或视频，从 `data.resultList[].url` 获取地址。`data.status=4` 表示失败。查看统一示例（辅助接口不在本skill范围）。

### 常见问题

- **模型不可用**：确认 `videoType` 使用上表中的公开名称，并确认当前账号可使用该模型。
- **视频时长报错**：Gemini Omni Flash、Seedance 2.5、可灵 V3-Omni、HappyHorse 仅允许 `-1` 或不传；Seedance 2.0、WAN3 仅允许模型支持的固定时长，不支持 `-1`。
- **未传时长后结果与预期不符**：跟随原视频模型（包括可灵 V3-Omni）会自动按 `-1` 处理；Seedance 2.0、WAN3 则取模型默认时长，未配置时回退 5 秒。
- **跟随原视频模型无法创建**：确认 `sourceVideoUrl` 可由服务端访问并能正确解析媒体时长；不要为这类模型传固定 `videoTime`。
- **无法读取原视频时长**：确认 URL 可公网访问、未过期，且返回的是可解析的视频内容。
- **参考图片数量超限**：数量上限按模型配置校验，具体见模型对照表；当前 Seedance 2.5 可传 30 张。
- **任务失败或长时间无结果**：检查视频、图片地址是否持续可访问，提示词是否合规，以及账户算力是否充足；素材超过模型支持范围也可能导致任务失败。

### 扣费标准

以下扣点从当前模型配置实时读取。

| 模型 | 扣费配置（点/秒） |
| --- | --- |
| doubao-seedance-2-5 （配置默认） | 按时长：**119** |
| gemini-omni-flash | 按时长：**33** |
| WAN3 | 按时长：支持有声 **35** |
| happyhorse-v2 | 按时长：**39** |
| kling-v3-omni | 按时长：**64** |
| doubao-seedance-2-0 | 按时长：**41** |

> 扣点数 = 单价（点/秒）× 计费时长（秒）。固定时长模型按 `videoTime` 计费；跟随原视频的模型按原视频实际时长向下取整计费。输出分辨率和比例由所选模型及原视频决定，参考图不额外增加扣点。


## curl示例

```bash
curl "${LINKFOX_TOOL_GATEWAY}/aigc/videoEditing" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H 'Content-Type: application/json' -H 'User-Agent: LinkFox-Skill/2.0' \
  --data '{"requestId": "video-edit-task-001", "params": {"sourceVideoUrl": "https://example.com/source.mp4", "prompt": "Change the background to a studio while preserving the product", "videoType": "kling-v3-omni"}}'
```

以上参数仅为结构示例；必须替换为真实素材、模型和本次任务ID，不能调用示例占位地址执行收费测试。

## 错误处理

HTTP200不保证业务成功。检查error、errcode及code；无成功字段时不要继续依赖链。处理400参数错误、401/403认证或归属失败、402余额不足、404任务不存在及下游错误。模板支持网关ToolErrorResponse XML标准化。不要只依赖脚本退出码，失败响应可能仍被保存为JSON。

未配置Key、401鉴权异常或402余额不足时，读取本skill内置 [onboarding.md](onboarding.md)，按原有AIGC流程引导。403成员归属或权限失败不能通过充值解决。手机号登录、短信及套餐支付按用户选择执行，不自动操作；不将登录Token、验证码或Key写入任务产物。

## Feedback

反馈接口：https://skill-api.linkfox.com/api/v1/public/feedback 。记录路径、requestId/taskId及脱敏错误摘要；参数类型不符、异常响应结构、持续查询失败可反馈。绝不包含Key、Authorization、Base64或私密素材内容。
