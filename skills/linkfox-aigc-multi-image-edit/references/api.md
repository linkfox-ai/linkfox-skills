# 多图融合修图 API 参考

## 调用规范

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/aigc/multiImageFusion`，网关未配置时回退正式网关。
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
| params.imageList | List<String> | 是 | 图片列表，请求张数见下方模型对照表；格式： jpg、jpeg、png、webp；大小： 单张不超过 10 MB；尺寸： 800×800～4096×4096|
| params.prompt | String | 否或条件必填 | 强化内容描述，用于补充说明图片融合目标和要求；最多 3000 个字符|
| params.provider | String | 是 | 模型，可选值详见比例与分辨率|
| params.outputNum | Integer | 否或条件必填 | 输出张数；默认 1 |
| params.template | String | 否或条件必填 | 提示词模板名称（多图模板），模板中的 provider、needOptimize 配置优先于入参可选值 搭配融图 / 搭配上身|
| params.needOptimize | Boolean | 否或条件必填 | 是否需要提示词优化，true：需要，false：不需要 |
| params.aspectRatio | String | 否或条件必填 | 输出比例，模型支持范围详见比例与分辨率|
| params.resolution | String | 否或条件必填 | 输出分辨率，详见比例与分辨率|
| params.supplyType | String | 否或条件必填 | 供应模式；是否支持该字段及可选值，以当前模型实际提供为准|
| params.quality | String | 否或条件必填 | 输出品质；仅适用于 GPT_2_IMAGE / GPT_2_5_IMAGE / GPT_2_5_F_IMAGE；GPT_2_IMAGE：low / medium / high；GPT_2_5_IMAGE / GPT_2_5_F_IMAGE：low / medium / high / xhigh / max；默认 medium|

## 公共任务上下文

请求外层只定义requestId、chatId、messageId、title、params。业务参数必须放params；成员和团队由服务端根据认证身份解析，不能靠memberId字段指定。chatId/messageId最长128字符。普通skill不发送渠道头时externalAgentPlatform默认skill；不要自行伪装workbuddy。

本分支实际下游创建路径：`/image/auth/agent/imagemake/multiImageFusion`。下方V3/V4文档仅说明params业务能力，不能据此更换实际调用路径。

## 响应与查询

创建返回taskId及costToken=0，0不代表免费。使用本目录scripts/query_task.py调用 `/aigc/taskQuery`，请求taskId及可选memberId，每次使用--no-cache。该查询也服务原有图像/视频任务，不存在本分支专属的makeTaskQuery接口。

查询响应字段：taskId、status（PROCESSING/SUCCESS/FAILED）、resultList、errorMsg、costToken。结果项仅定义id、url、type；type取自下游extendField.type。当前后端不返回单项status/errorCode/errorMsg、width/height/format/size、完整extendField或containsSyntheticPerformer；skill不得推断未返回的信息，也不能通过查询传format或containsSyntheticPerformer。

费用仍由下游处理，count按2000倍换算。官方脚本保留响应头X-Cost-Token/X-Cost-Credit提供的实际费用，不使用创建时的0覆盖查询费用。没有费用时表示未知。

## 素材准备

本地图片或视频读取并按内置 [file-upload.md](file-upload.md)执行上传。外部URL也必须先下载上传，生成接口只使用上传返回的viewUrl。仅处理本次接口实际需要的素材：视频翻译不要求额外上传图片，视频编辑的参考图片可选。

## 下游业务字段及模型参考

以下为已下载的业务文档，仅作为字段、模型限制及业务条件参考。其中下游id/status/count/响应封装不能替代上方网关taskId/status/costToken契约；文档里的单项扩展字段当前未由网关结果VO透出。

# 智能修图-多图 V3

多图融合智能修图接口。

**下游 POST** `/image/v3/make/multiImageFusion`  
Content-Type: `application/json`

### 请求体

#### 基础参数

| 参数 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| imageList | array[string] | 必填 | 图片列表，请求张数见[下方模型对照表](#比例与分辨率)<br>格式： jpg、jpeg、png、webp；大小： 单张不超过 10 MB；尺寸： 800×800～4096×4096 |
| prompt | string | 可选 | 强化内容描述，用于补充说明图片融合目标和要求；最多 3000 个字符 |
| provider | string | 必填 | 模型，可选值详见[比例与分辨率](#比例与分辨率) |
| outputNum | integer | 可选 | 输出张数；默认 1 |
| template | string | 可选 | 提示词模板名称（多图模板），模板中的 provider、needOptimize 配置优先于入参**可选值** `搭配融图` / `搭配上身` |
| needOptimize | boolean | 可选 | 是否需要提示词优化，true：需要，false：不需要 |
| aspectRatio | string | 可选 | 输出比例，模型支持范围详见[比例与分辨率](#比例与分辨率) |
| resolution | string | 可选 | 输出分辨率，详见[比例与分辨率](#比例与分辨率) |
| supplyType | string | 可选 | 供应模式；是否支持该字段及可选值，以当前模型实际提供为准 |
| quality | string | 可选 | 输出品质；仅适用于 `GPT_2_IMAGE` / `GPT_2_5_IMAGE` / `GPT_2_5_F_IMAGE`<br>GPT_2_IMAGE：low / medium / high；GPT_2_5_IMAGE / GPT_2_5_F_IMAGE：low / medium / high / xhigh / max；默认 medium |

#### GPT_2_5_IMAGE / GPT_2_5_F_IMAGE 使用限制

- 支持比例：1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21；支持分辨率：1K / 2K / 4K，默认 2K

#### QWEN_IMAGE_3_PRO 使用限制

- 支持 JPG、JPEG、PNG、WEBP 格式，单张图片不超过 10 MB；建议宽高在 384～2048 像素范围内。

### 比例与分辨率

| provider | 支持比例 | 支持分辨率 | 默认分辨率 | 请求图片 |
| --- | --- | --- | --- | --- |
| BANANA | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K | 1K | 1～3 张 |
| BANANA_2_LITE | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 9:16 / 16:9 / 21:9 | 1K | 1K | 1～10 张 |
| BANANA_2 | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K / 4K | 2K | 1～10 张 |
| BANANA_PRO | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K / 2K / 4K | 2K | 1～10 张 |
| WAN2_7 | 1:1 / 1:4 / 4:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K | 2K | 1～9 张 |
| QWEN_IMAGE_3_PRO | 1:1 / 1:4 / 4:1 / 1:8 / 8:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 / 9:21 | 1K / 2K | 2K | 1～3 张 |
| SEEDREAM5_PRO | 1:1 / 3:4 / 4:3 / 9:16 / 16:9 / 3:2 / 2:3 / 21:9 | 1K / 2K | 2K | 1～10 张 |
| GPT_2_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 4:5 / 5:4 / 9:16 / 16:9 / 9:21 / 21:9 | 1K / 2K / 4K | 2K | 1～6 张 |
| GPT_2_5_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～10 张 |
| GPT_2_5_F_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～10 张 |
| AIDRAW_EDIT | 1:1 / 2:3 / 3:2 / 3:4 / 4:3 / 9:16 / 16:9 / 21:9 | 1K / 2K | 2K | 1～4 张 |

### 请求示例

**GPT 系列**

可选 provider：`GPT_2_IMAGE`、`GPT_2_5_IMAGE`、`GPT_2_5_F_IMAGE`（其余参数相同）

```json
{
    "imageList": [
        "https://test-file-ai.linkfox.com/UPLOAD/image1.jpg",
        "https://test-file-ai.linkfox.com/UPLOAD/image2.jpg"
    ],
    "prompt": "融合两张图片风格，保留主体元素",
    "provider": "GPT_2_IMAGE",
    "outputNum": 1,
    "resolution": "2K",
    "aspectRatio": "1:1",
    "quality": "high",
    "supplyType": "stable",
    "needOptimize": true
}
```

**BANANA_PRO**

```json
{
    "imageList": [
        "https://test-file-ai.linkfox.com/UPLOAD/image1.jpg",
        "https://test-file-ai.linkfox.com/UPLOAD/image2.jpg"
    ],
    "prompt": "融合两张图片风格，保留主体元素",
    "provider": "BANANA_PRO",
    "outputNum": 1,
    "resolution": "2K",
    "aspectRatio": "1:1",
    "supplyType": "stable",
    "needOptimize": true
}
```

**QWEN_IMAGE_3_PRO**

```json
{
    "imageList": [
        "https://test-file-ai.linkfox.com/UPLOAD/image1.jpg",
        "https://test-file-ai.linkfox.com/UPLOAD/image2.jpg"
    ],
    "prompt": "融合两张图片风格，保留主体元素",
    "provider": "QWEN_IMAGE_3_PRO",
    "outputNum": 1,
    "resolution": "2K",
    "aspectRatio": "1:1",
    "supplyType": "stable",
    "needOptimize": true
}
```

### 提交后返回什么

提交成功后返回任务编号 `data.id`，表示任务已创建，结果还需等待生成。请保存编号。查看返回示例（辅助接口不在本skill范围）。

### 查询生成结果

用任务编号 `data.id` 调用获取作图结果（辅助接口不在本skill范围），每次查询至少间隔 10 秒。`data.status=3` 表示成功；若生成了图片或视频，从 `data.resultList[].url` 获取地址。`data.status=4` 表示失败。查看统一示例（辅助接口不在本skill范围）。

### 扣费标准

以下扣点从当前模型配置实时读取。

| 模型 | 扣费配置（点/张，经济 / 稳定） |
| --- | --- |
| GPT_2_5_IMAGE （配置默认） | 1K：low **稳** 4；medium **稳** 30；high **稳** 120；xhigh **稳** 150；max **稳** 200<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150；xhigh **稳** 240；max **稳** 280<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300；xhigh **稳** 330；max **稳** 360 |
| GPT_2_5_F_IMAGE | 1K：low **稳** 4；medium **稳** 30；high **稳** 120；xhigh **稳** 150；max **稳** 200<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150；xhigh **稳** 240；max **稳** 280<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300；xhigh **稳** 330；max **稳** 360 |
| GPT_2_IMAGE | 1K：low **稳** 4；medium **稳** 30；high **稳** 120<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300 |
| BANANA_PRO | 1K：**经** 40 **稳** 60<br>2K：**经** 40 **稳** 60<br>4K：**经** 70 **稳** 90 |
| BANANA_2 | 1K：**经** 30 **稳** 50<br>2K：**经** 40 **稳** 60<br>4K：**经** 50 **稳** 70 |
| BANANA_2_LITE | 1K：**稳** 25 |
| BANANA | 1K：**经** 20 **稳** 40 |
| SEEDREAM5_PRO | 1K：**稳** 25<br>2K：**稳** 50 |
| AIDRAW_EDIT | 1K：**稳** 25<br>2K：**稳** 25 |
| QWEN_IMAGE_3_PRO | 1K：**稳** 25<br>2K：**稳** 40 |
| WAN2_7 | 1K：**稳** 30<br>2K：**稳** 30 |

> 扣点数 = 单张扣点 × 输出数量（`outputNum`）。


## curl示例

```bash
curl "${LINKFOX_TOOL_GATEWAY}/aigc/multiImageFusion" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H 'Content-Type: application/json' -H 'User-Agent: LinkFox-Skill/2.0' \
  --data '{"params": {"imageList": ["https://example.com/product.png", "https://example.com/scene.png"], "prompt": "Place the product into the reference scene", "provider": "GPT_2_5_IMAGE"}}'
```

以上参数仅为结构示例；必须替换为真实素材和模型，不能调用示例占位地址执行收费测试。

## 错误处理

HTTP200不保证业务成功。检查error、errcode及code；无成功字段时不要继续依赖链。处理400参数错误、401/403认证或归属失败、402余额不足、404任务不存在及下游错误。模板支持网关ToolErrorResponse XML标准化。不要只依赖脚本退出码，失败响应可能仍被保存为JSON。

未配置Key、401鉴权异常或402余额不足时，读取本skill内置 [onboarding.md](onboarding.md)，按原有AIGC流程引导。403成员归属或权限失败不能通过充值解决。手机号登录、短信及套餐支付按用户选择执行，不自动操作；不将登录Token、验证码或Key写入任务产物。

## Feedback

反馈接口：https://skill-api.linkfox.com/api/v1/public/feedback 。记录路径、requestId/taskId及脱敏错误摘要；参数类型不符、异常响应结构、持续查询失败可反馈。绝不包含Key、Authorization、Base64或私密素材内容。
