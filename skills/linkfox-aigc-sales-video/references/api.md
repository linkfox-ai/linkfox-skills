# 带货口播视频 API 参考

## 调用规范

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/aigc/salesVideo`，网关未配置时回退正式网关。
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
| params.videoType | String | 是 | 模型类型：minimax-h3-lite、minimax-h3、wan3、doubao-seedance-2-5、doubao-seedance-2-0、doubao-seedance-2-0-fast、doubao-seedance-2-0-mini、happyhorse-v2|
| params.prompt | String | 是 | 口播脚本/视频提示词。建议包含：产品卖点、使用场景、人群、语气风格|
| params.imageList | List<String> | 是 | 参考图列表（商品图、场景图、品牌图等），至少 1 张可访问外网的图片 URL；数量上限按模型区分，见下方各模型参数支持情况|
| params.videoTime | Integer | 否或条件必填 | 视频时长（秒），不同类型支持的时长不同，见下方各模型参数支持情况 |
| params.resolution | String | 否或条件必填 | 视频分辨率。详见各模型参数支持情况|
| params.aspectRatio | String | 否或条件必填 | 视频比例：16:9 / 9:16 / 1:1 / 4:3 / 3:4 / 21:9；不传则使用模型默认值|
| params.isPro | Boolean | 否或条件必填 | 是否开启高质量模式；适用于 doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / doubao-seedance-2-5，未传 resolution 时，true 使用 720p；默认 false |

## 公共任务上下文

请求外层只定义requestId、chatId、messageId、title、params。业务参数必须放params；成员和团队由服务端根据认证身份解析，不能靠memberId字段指定。chatId/messageId最长128字符。普通skill不发送渠道头时externalAgentPlatform默认skill；不要自行伪装workbuddy。

本分支实际下游创建路径：`/image/auth/agent/imagemake/salesVideo`。下方V3/V4文档仅说明params业务能力，不能据此更换实际调用路径。

## 响应与查询

创建返回taskId及costToken=0，0不代表免费。使用本目录scripts/query_task.py调用 `/aigc/taskQuery`，请求taskId及可选memberId，每次使用--no-cache。该查询也服务原有图像/视频任务，不存在本分支专属的makeTaskQuery接口。

查询响应字段：taskId、status（PROCESSING/SUCCESS/FAILED）、resultList、errorMsg、costToken。结果项仅定义id、url、type；type取自下游extendField.type。当前后端不返回单项status/errorCode/errorMsg、width/height/format/size、完整extendField或containsSyntheticPerformer；skill不得推断未返回的信息，也不能通过查询传format或containsSyntheticPerformer。

费用仍由下游处理，count按2000倍换算。官方脚本保留响应头X-Cost-Token/X-Cost-Credit提供的实际费用，不使用创建时的0覆盖查询费用。没有费用时表示未知。

## 素材准备

本地图片或视频读取并按内置 [file-upload.md](file-upload.md)执行上传。外部URL也必须先下载上传，生成接口只使用上传返回的viewUrl。仅处理本次接口实际需要的素材：视频翻译不要求额外上传图片，视频编辑的参考图片可选。

## 下游业务字段及模型参考

以下为已下载的业务文档，仅作为字段、模型限制及业务条件参考。其中下游id/status/count/响应封装不能替代上方网关taskId/status/costToken契约；文档里的单项扩展字段当前未由网关结果VO透出。

# 带货口播 V3

用于生成带商品卖点讲解的口播视频，适合电商上新、活动促销、详情页素材补充等场景。

**下游 POST** `/image/v3/make/salesVideo`  
Content-Type: `application/json`

### 请求体

| 参数 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| videoType | string | 必填 | 模型类型：`minimax-h3-lite`、`minimax-h3`、`wan3`、`doubao-seedance-2-5`、`doubao-seedance-2-0`、`doubao-seedance-2-0-fast`、`doubao-seedance-2-0-mini`、`happyhorse-v2` |
| prompt | string | 必填 | 口播脚本/视频提示词。建议包含：产品卖点、使用场景、人群、语气风格 |
| imageList | array | 必填 | 参考图列表（商品图、场景图、品牌图等），至少 1 张可访问外网的图片 URL；数量上限按模型区分，见下方[各模型参数支持情况](#各模型参数支持情况) |
| videoTime | integer | 可选 | 视频时长（秒），不同类型支持的时长不同，见下方[各模型参数支持情况](#各模型参数支持情况) |
| resolution | string | 可选 | 视频分辨率。详见[各模型参数支持情况](#各模型参数支持情况) |
| aspectRatio | string | 可选 | 视频比例：16:9 / 9:16 / 1:1 / 4:3 / 3:4 / 21:9<br>不传则使用模型默认值 |
| isPro | boolean | 可选 | 是否开启高质量模式；适用于 doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / doubao-seedance-2-5，未传 `resolution` 时，`true` 使用 720p；默认 false |

---

### 各模型参数支持情况

| 模型 | 分辨率 | 时长（秒） | 参考图上限 |
| --- | --- | --- | --- |
| minimax-h3-lite | 768P | 5/10/15 | 9 |
| minimax-h3 | 768P / 2K | 5/10/15 | 9 |
| wan3 | 480P / 720P / 1080P | 5/10/15/20/25/30 | 10 |
| doubao-seedance-2-5 | 480P / 720P / 1080P | 5/10/15/20/25/30 | 30 |
| doubao-seedance-2-0 | 480P / 720P / 1080P | 5/10/15 | 9 |
| doubao-seedance-2-0-fast | 480P / 720P | 5/10/15 | 9 |
| doubao-seedance-2-0-mini | 480P / 720P | 5/10/15 | 9 |
| happyhorse-v2 | 720P / 1080P | 5/10/15 | 9 |

---

### 参数使用建议

- `prompt` 建议明确：商品名称 + 核心卖点 + 目标人群 + 结尾行动指令（如"立即下单"）。
- `imageList` 必填，传入商品主图/细节图通常能提升一致性和转化表达。
- `videoType` 与 `videoTime` 建议组合测试：不同渠道（短视频/详情页）可选择不同时长。
- 使用 doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / doubao-seedance-2-5 且未传 `resolution` 时，可通过 `isPro=true` 使用 720p。
- `happyhorse-v2` 分辨率默认 720p，如需更高清可传 `resolution: "1080p"`。

---

### 请求示例

**doubao-seedance-2-0**

#### 示例1：doubao-seedance-2-0

```json
{
  "videoType": "doubao-seedance-2-0",
  "prompt": "这款便携式榨汁杯，300W强劲电机，40秒快速出汁，Type-C充电，通勤健身都能用。现在下单享限时优惠。",
  "imageList": [
    "https://example.com/product-main.jpg",
    "https://example.com/product-detail.jpg"
  ],
  "videoTime": 10,
  "resolution": "1080P",
  "aspectRatio": "9:16",
  "isPro": true
}
```

**happyhorse-v2**

#### 示例2：happyhorse-v2

```json
{
  "videoType": "happyhorse-v2",
  "prompt": "精选有机坚果礼盒，多种坚果搭配，健康美味送人有面子。",
  "imageList": [
    "https://example.com/gift-box.jpg",
    "https://example.com/nuts-detail.jpg",
    "https://example.com/packaging.jpg"
  ],
  "videoTime": 15,
  "resolution": "1080P",
  "aspectRatio": "16:9"
}
```

**doubao-seedance-2-0-fast**

#### 示例3：doubao-seedance-2-0-fast

```json
{
  "videoType": "doubao-seedance-2-0-fast",
  "prompt": "新品上市，限时优惠，手慢无。",
  "imageList": [
    "https://example.com/product.jpg"
  ],
  "videoTime": 5,
  "resolution": "480P",
  "aspectRatio": "9:16"
}
```

**doubao-seedance-2-5**

#### 示例4：doubao-seedance-2-5（豆包 Seedance 2.5）— 30 秒长视频

```json
{
  "videoType": "doubao-seedance-2-5",
  "prompt": "这款智能手表，支持心率监测、睡眠追踪、运动记录，50米防水设计，续航长达7天。多种表盘可选，时尚百搭。现在购买赠送额外表带，立享优惠价。",
  "imageList": [
    "https://example.com/watch-main.jpg",
    "https://example.com/watch-side.jpg",
    "https://example.com/watch-screen.jpg",
    "https://example.com/watch-strap.jpg"
  ],
  "videoTime": 30,
  "resolution": "720P",
  "aspectRatio": "16:9"
}
```

---

### 提交后返回什么

提交成功后返回任务编号 `data.id`，表示任务已创建，结果还需等待生成。请保存编号。查看返回示例（辅助接口不在本skill范围）。

### 查询生成结果

用任务编号 `data.id` 调用获取作图结果（辅助接口不在本skill范围），每次查询至少间隔 10 秒。`data.status=3` 表示成功；若生成了图片或视频，从 `data.resultList[].url` 获取地址。`data.status=4` 表示失败。查看统一示例（辅助接口不在本skill范围）。

### 常见问题

- **报参数错误**：优先检查 `videoType` 是否为支持值（minimax-h3-lite / minimax-h3 / wan3 / doubao-seedance-2-5 / doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / happyhorse-v2），`videoTime` 是否匹配该类型的可选时长。
- **doubao-seedance-2-0-fast / doubao-seedance-2-0-mini 报分辨率错误**：两者均不支持 `1080p`，请传 `480p` 或 `720p`。
- **任务失败**：检查提示词是否违规、图片地址是否可访问、套餐算力是否充足。
- **结果为空或超时**：延长轮询时间，复杂内容通常生成耗时更长。

### 扣费标准

以下扣点从当前模型配置实时读取。

| 模型 | 扣费配置（点） |
| --- | --- |
| minimax-h3-lite （配置默认） | 768P：5秒 **15**；10秒 **30**；15秒 **45**<br>2K：5秒 **40**；10秒 **80**；15秒 **120** |
| wan3 | 480P：支持有声；5秒 **90**；10秒 **180**；15秒 **270**；20秒 **360**；25秒 **450**；30秒 **540**<br>720P：支持有声；5秒 **175**；10秒 **350**；15秒 **525**；20秒 **700**；25秒 **875**；30秒 **1050**<br>1080P：支持有声；5秒 **355**；10秒 **710**；15秒 **1065**；20秒 **1420**；25秒 **1775**；30秒 **2130** |
| doubao-seedance-2-5 | 480P：5秒 **265**；10秒 **530**；15秒 **795**；20秒 **1060**；25秒 **1325**；30秒 **1590**<br>720P：5秒 **595**；10秒 **1190**；15秒 **1785**；20秒 **2380**；25秒 **2975**；30秒 **3570**<br>1080P：5秒 **1620**；10秒 **3240**；15秒 **4860**；20秒 **6480**；25秒 **8100**；30秒 **9720** |
| doubao-seedance-2-0-fast | 480P：5秒 **105**；10秒 **210**；15秒 **315**<br>720P：5秒 **215**；10秒 **430**；15秒 **645** |
| doubao-seedance-2-0-mini | 480P：5秒 **35**；10秒 **70**；15秒 **105**<br>720P：5秒 **70**；10秒 **140**；15秒 **210** |
| happyhorse-v2 | 720P：5秒 **185**；10秒 **370**；15秒 **555**<br>1080P：5秒 **240**；10秒 **480**；15秒 **720** |
| doubao-seedance-2-0 | 480P：5秒 **200**；10秒 **400**；15秒 **600**<br>720P：5秒 **400**；10秒 **800**；15秒 **1200**<br>1080P：5秒 **1500**；10秒 **3000**；15秒 **4500** |
| minimax-h3 | 768P：5秒 **200**；10秒 **400**；15秒 **600**<br>2K：5秒 **320**；10秒 **640**；15秒 **960** |

> 按模型、分辨率和视频时长扣点。


## curl示例

```bash
curl "${LINKFOX_TOOL_GATEWAY}/aigc/salesVideo" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H 'Content-Type: application/json' -H 'User-Agent: LinkFox-Skill/2.0' \
  --data '{"params": {"videoType": "doubao-seedance-2-5", "prompt": "Explain the portable bottle and demonstrate its lid", "imageList": ["https://example.com/product.png"], "videoTime": 5}}'
```

以上参数仅为结构示例；必须替换为真实素材和模型，不能调用示例占位地址执行收费测试。

## 错误处理

HTTP200不保证业务成功。检查error、errcode及code；无成功字段时不要继续依赖链。处理400参数错误、401/403认证或归属失败、402余额不足、404任务不存在及下游错误。模板支持网关ToolErrorResponse XML标准化。不要只依赖脚本退出码，失败响应可能仍被保存为JSON。

未配置Key、401鉴权异常或402余额不足时，读取本skill内置 [onboarding.md](onboarding.md)，按原有AIGC流程引导。403成员归属或权限失败不能通过充值解决。手机号登录、短信及套餐支付按用户选择执行，不自动操作；不将登录Token、验证码或Key写入任务产物。

## Feedback

反馈接口：https://skill-api.linkfox.com/api/v1/public/feedback 。记录路径、requestId/taskId及脱敏错误摘要；参数类型不符、异常响应结构、持续查询失败可反馈。绝不包含Key、Authorization、Base64或私密素材内容。
