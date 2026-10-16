# 服装营销套图 API 参考

## 调用规范

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/aigc/wearCollection`，网关未配置时回退正式网关。
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
| params.imageList | List<String> | 是 | 商品图片列表，请求张数见下方模型对照表；格式： jpg/jpeg/png/webp；大小： 单张≤10M；尺寸： 384×384～4096×4096|
| params.sellerPoint | String | 否或条件必填 | 商品卖点描述，≤2500字符（未开启自动提取时必填）|
| params.isExtractPrePoint | Boolean | 否或条件必填 | 自动提取卖点；默认 false |
| params.provider | String | 否或条件必填 | 未传时使用当前业务类型的默认启用模型；模型选择，可选值及默认分辨率见比例与分辨率；模型特殊参数；当前默认 GPT_2_5_IMAGE|
| params.aspectRatio | String | 否或条件必填 | 素材宽高比（卖点图/模特图/种草图等），按模型配置校验，支持比例详见比例与分辨率|
| params.resolution | String | 否或条件必填 | 输出分辨率，详情见比例与分辨率|
| params.brandKey | BrandKey | 否或条件必填 | 品牌基因 JSON 对象 |
| params.modelTypeNum | Integer | 否或条件必填 | 模特图数量，最大12；默认 0 |
| params.sellerTypeNum | Integer | 否或条件必填 | 卖点图数量，最大12；默认 0 |
| params.insTypeNum | Integer | 否或条件必填 | 种草图数量，最大12；默认 0 |
| params.sizeTypeNum | Integer | 否或条件必填 | 尺码图数量，最大12；默认 0 |
| params.whiteTypeNum | Integer | 否或条件必填 | 白底图数量，最大12；默认 0 |
| params.aPlusNum | Integer | 否或条件必填 | 普通A+数量，最大12；默认 0 |
| params.aPlusProNum | Integer | 否或条件必填 | 高级A+数量（Pro版），最大12；默认 0 |
| params.aPlusHasPhone | Boolean | 否或条件必填 | 是否生成手机版A+（基于高级A+结果，数量与高级A+一致）；默认 false |
| params.aPlusAspectRatio | String | 否或条件必填 | A+页面宽高比，不填则自动选择；支持格式：16:9、9:16、1:1、1:3.7|
| params.modelImageUrl | String | 否或条件必填 | 模特参考图，未设置时启动智能模式|
| params.sceneImageUrl | String | 否或条件必填 | 场景参考图，未设置时启动智能模式|
| params.isExactScene | Boolean | 否或条件必填 | 场景裂变模式：true 遵循背景 false 相似裂变；默认 true |
| params.modelAndSceneInfo | String | 否或条件必填 | 可选：描述想要生成的场景内容和模特特征|
| params.noText | Boolean | 否或条件必填 | 无字模式，开启后排版不含文字，仅输出纯图片素材；默认 false |
| params.aPlusStyles | List<LayoutStyle> | 否或条件必填 | A+图排版列表，为每张A+图指定排版方式；数量需不少于A+图数量（aPlusNum + aPlusProNum），每项可填 id 或 prompt|
| params.pointStyles | List<LayoutStyle> | 否或条件必填 | 卖点图排版列表，为每张卖点图指定排版方式；数量需不少于卖点图数量（sellerTypeNum），每项可填 id 或 prompt|
| params.sensitiveLibraryId | Long | 否或条件必填 | 敏感词库ID，命中的敏感词会经AI改写规避；不传则不启用该能力 |
| params.replaceLibraryId | Long | 否或条件必填 | 替换词库ID，命中的词按预设替换词直接替换；不传则不启用该能力 |
| params.quality | String | 否或条件必填 | 输出品质；仅适用于 GPT_2_IMAGE / GPT_2_5_IMAGE / GPT_2_5_F_IMAGE；GPT_2_IMAGE：low / medium / high；GPT_2_5_IMAGE / GPT_2_5_F_IMAGE：low / medium / high / xhigh / max；默认 medium|

## 公共任务上下文

请求外层只定义requestId、chatId、messageId、title、params。业务参数必须放params；成员和团队由服务端根据认证身份解析，不能靠memberId字段指定。chatId/messageId最长128字符。普通skill不发送渠道头时externalAgentPlatform默认skill；不要自行伪装workbuddy。

本分支实际下游创建路径：`/image/auth/agent/imagemake/wearCollection`。下方V3/V4文档仅说明params业务能力，不能据此更换实际调用路径。

## 响应与查询

创建返回taskId及costToken=0，0不代表免费。使用本目录scripts/query_task.py调用 `/aigc/taskQuery`，请求taskId及可选memberId，每次使用--no-cache。该查询也服务原有图像/视频任务，不存在本分支专属的makeTaskQuery接口。

查询响应字段：taskId、status（PROCESSING/SUCCESS/FAILED）、resultList、errorMsg、costToken。结果项仅定义id、url、type；type取自下游extendField.type。当前后端不返回单项status/errorCode/errorMsg、width/height/format/size、完整extendField或containsSyntheticPerformer；skill不得推断未返回的信息，也不能通过查询传format或containsSyntheticPerformer。

费用仍由下游处理，count按2000倍换算。官方脚本保留响应头X-Cost-Token/X-Cost-Credit提供的实际费用，不使用创建时的0覆盖查询费用。没有费用时表示未知。

## 素材准备

本地图片或视频读取并按内置 [file-upload.md](file-upload.md)执行上传。外部URL也必须先下载上传，生成接口只使用上传返回的viewUrl。仅处理本次接口实际需要的素材：视频翻译不要求额外上传图片，视频编辑的参考图片可选。

## 下游业务字段及模型参考

以下为已下载的业务文档，仅作为字段、模型限制及业务条件参考。其中下游id/status/count/响应封装不能替代上方网关taskId/status/costToken契约；文档里的单项扩展字段当前未由网关结果VO透出。

# 服装套图 V3

生成服装套图，支持排版素材和卖点分析。

**下游 POST** `/image/v3/make/wearCollection`  
Content-Type: `application/json`

### 请求体

#### 基础参数

| 参数 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| imageList | array[string] | 必填 | 商品图片列表，请求张数见[下方模型对照表](#比例与分辨率)<br>格式： jpg/jpeg/png/webp；大小： 单张≤10M；尺寸： 384×384～4096×4096 |
| sellerPoint | string | 条件必填 | 商品卖点描述，≤2500字符（未开启自动提取时必填） |
| isExtractPrePoint | boolean | 可选 | 自动提取卖点；默认 false |
| provider | string | 可选 | 未传时使用当前业务类型的默认启用模型；模型选择，可选值及默认分辨率见[比例与分辨率](#比例与分辨率)；[模型特殊参数](#模型特殊参数)；当前默认 GPT_2_5_IMAGE |
| aspectRatio | string | 可选 | 素材宽高比（卖点图/模特图/种草图等），按模型配置校验，支持比例详见[比例与分辨率](#比例与分辨率) |
| resolution | string | 可选 | 输出分辨率，详情见[比例与分辨率](#比例与分辨率) |
| brandKey | object | 可选 | 品牌基因 JSON 对象 |
| ↳ brandColor |  |  | 品牌颜色（格式：#RRGGBB，例：#0775FA） |
| ↳ fontStyle |  |  | 字体风格（兼容无衬线体，硬性无衬线体，优雅衬线体） |
| ↳ salesRegion |  |  | 销售地区（例：中东欧） |
| ↳ language |  |  | 语言（例：英语西班牙语） |
| ↳ platform |  |  | 平台（例：亚马逊） |
| ↳ customSettings |  |  | 自定义描述内容 |

#### 出图数量

至少选择一种图片类型，将对应的出图数量设为 1 或以上；可同时选择多种，未填写的数量按 0 计算。

| 参数 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| modelTypeNum | integer | 可选 | 模特图数量，最大12；默认 0 |
| sellerTypeNum | integer | 可选 | 卖点图数量，最大12；默认 0 |
| insTypeNum | integer | 可选 | 种草图数量，最大12；默认 0 |
| sizeTypeNum | integer | 可选 | 尺码图数量，最大12；默认 0 |
| whiteTypeNum | integer | 可选 | 白底图数量，最大12；默认 0 |
| aPlusNum | integer | 可选 | 普通A+数量，最大12；默认 0 |
| aPlusProNum | integer | 可选 | 高级A+数量（Pro版），最大12；默认 0 |
| aPlusHasPhone | boolean | 可选 | 是否生成手机版A+（基于高级A+结果，数量与高级A+一致）；默认 false |
| aPlusAspectRatio | string | 可选 | A+页面宽高比，不填则自动选择；支持格式：16:9、9:16、1:1、1:3.7 |

#### 模特与场景

| 参数 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| modelImageUrl | string | 可选 | 模特参考图，未设置时启动智能模式 |
| sceneImageUrl | string | 可选 | 场景参考图，未设置时启动智能模式 |
| isExactScene | boolean | 可选 | 场景裂变模式：true 遵循背景 false 相似裂变；默认 true |
| modelAndSceneInfo | string | 可选 | 可选：描述想要生成的场景内容和模特特征 |

#### 排版样式

| 参数 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| noText | boolean | 可选 | 无字模式，开启后排版不含文字，仅输出纯图片素材；默认 false |
| aPlusStyles | List | 可选 | A+图排版列表，为每张A+图指定排版方式<br>数量需不少于A+图数量（`aPlusNum` + `aPlusProNum`），每项可填 `id` 或 `prompt` |
| pointStyles | List | 可选 | 卖点图排版列表，为每张卖点图指定排版方式<br>数量需不少于卖点图数量（`sellerTypeNum`），每项可填 `id` 或 `prompt` |

> `id` ：通过作图素材（辅助接口不在本skill范围）接口获取（type=10：套图-排版素材），自动取该素材对应的提示词、排版图与缩略图
>
> `prompt` ：通过图片获取描述词（辅助接口不在本skill范围）接口获取（type=69：穿衣套图卖点分析），作为该图的排版提示词下发给模型
>
> 本示例中的 `aPlusStyles` 使用接口返回的 A+ 横板排版 ID；`pointStyles` 使用服装排版（C 系列）ID。排版 ID 需以当前环境中 `type=IMAGE_LAYOUT` 返回的数据为准。
>
> 不传当前参数时使用默认排版，不校验数量。

#### 手动上传排版并提取提示词

如果没有现成的排版素材 ID，也可以先上传自己的排版图片，再提取提示词传入套图接口：

1. 将排版图片上传到可访问的文件地址，得到 `layoutImageUrl`。上传接口以平台当前文件上传能力为准，本接口不接收图片文件本身。
2. 调用图片获取描述词-创建任务（辅助接口不在本skill范围），使用服装套图类型 `69`，并指定 `provider` 为 `API_LAYOUT_DESC`：

1. 使用创建任务返回的 `data.id` 调用图片获取描述词-获取结果（辅助接口不在本skill范围），轮询至 `data.status=3`，读取 `data.result.content`。
2. 将提取结果作为排版提示词传入 `aPlusStyles` 或 `pointStyles`，例如：

如果排版已通过作图素材接口登记为 `type=10`，则直接传素材返回的 `id`；系统会自动读取该素材关联的排版图和提示词。手动上传图片不会自动成为排版素材，也不能把图片 URL 直接填入 `aPlusStyles` 或 `pointStyles`。

#### 词库

| 参数 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| sensitiveLibraryId | Long | 可选 | 敏感词库ID，命中的敏感词会经AI改写规避<br>不传则不启用该能力 |
| replaceLibraryId | Long | 可选 | 替换词库ID，命中的词按预设替换词直接替换<br>不传则不启用该能力 |

> `sensitiveLibraryId`：通过作图素材（辅助接口不在本skill范围）接口获取（type=11：敏感词库），取列表中的 `id` 字段
>
> `replaceLibraryId`：通过作图素材（辅助接口不在本skill范围）接口获取（type=12：替换词库），取列表中的 `id` 字段
>
> 两个词库互相独立，可单独传入其中之一，也可同时传入。
>
> 同时传入时依次执行：先用敏感词库检测并经AI改写规避，再按替换词库做替换。替换不依赖改写结果——无论敏感词是否命中、AI改写是否成功，只要传了替换词库就会执行替换。
>
> 传入不存在、无权访问，或类型与参数不匹配的ID时，返回参数校验错误。

#### 模型特殊参数

| 参数 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| quality | string | 可选 | 输出品质；仅适用于 `GPT_2_IMAGE` / `GPT_2_5_IMAGE` / `GPT_2_5_F_IMAGE`<br>GPT_2_IMAGE：low / medium / high<br>GPT_2_5_IMAGE / GPT_2_5_F_IMAGE：low / medium / high / xhigh / max；默认 medium |

### 比例与分辨率

| provider | 支持比例 | 支持分辨率 | 默认分辨率 | 请求图片 |
| --- | --- | --- | --- | --- |
| BANANA_2 | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K / 4K | 2K | 1～5 张 |
| BANANA_2_LITE | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 9:16 / 16:9 / 21:9 | 1K | 1K | 1～5 张 |
| BANANA_PRO | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K / 2K / 4K | 2K | 1～5 张 |
| WAN2_7 | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K | 2K | 1～5 张 |
| SEEDREAM5_PRO | 1:1 / 3:4 / 4:3 / 9:16 / 16:9 / 3:2 / 2:3 / 21:9 | 1K / 2K | 2K | 1～5 张 |
| GPT_2_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～5 张 |
| GPT_2_5_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～5 张 |
| GPT_2_5_F_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～5 张 |

### 请求示例

**GPT 系列**

可选 provider：`GPT_2_IMAGE`、`GPT_2_5_IMAGE`、`GPT_2_5_F_IMAGE`（其余参数相同）

```json
{
  "imageList": ["https://test-file-ai.linkfox.com/UPLOAD/MANAGE/7c6b7c7010564aba919ad89dabce4f82.jpg"],
  "sellerPoint": "时尚优雅的女士连衣裙，气质高雅，适合多种场合穿搭",
  "provider": "GPT_2_IMAGE",
  "resolution": "2K",
  "quality": "high",
  "aPlusNum": 1,
  "sellerTypeNum": 1,
  "aPlusStyles": [{"id":"2015989768887762944"}],
  "pointStyles": [{"id":"2095034520741818370"}]
}
```

**BANANA_PRO**

```json
{
  "imageList": ["https://test-file-ai.linkfox.com/UPLOAD/MANAGE/7c6b7c7010564aba919ad89dabce4f82.jpg"],
  "sellerPoint": "时尚优雅的女士连衣裙，气质高雅，适合多种场合穿搭",
  "provider": "BANANA_PRO",
  "resolution": "2K",
  "aPlusNum": 1,
  "sellerTypeNum": 1,
  "aPlusStyles": [{"id":"2015989768887762944"}],
  "pointStyles": [{"id":"2095034520741818370"}]
}
```

### 提交后返回什么

提交成功后返回任务编号 `data.id`，表示任务已创建，结果还需等待生成。请保存编号。查看返回示例（辅助接口不在本skill范围）。

### 查询生成结果

用任务编号 `data.id` 调用获取作图结果（辅助接口不在本skill范围），每次查询至少间隔 10 秒。`data.status=3` 表示成功；若生成了图片或视频，从 `data.resultList[].url` 获取地址。`data.status=4` 表示失败。查看统一示例（辅助接口不在本skill范围）。

### 结果图片的素材类型

查询响应结果时，每张图的 `extendField.type` 字段标明该图属于哪类素材，便于分类识别：

| type 值 | 说明 |
| --- | --- |
| A+ | 普通A+：A+页面图文营销模块 |
| APlusPro | 高级A+：A+页面高级图文模块，支持自定义宽高比 |
| APlusHasPhone | 手机版A+：基于高级A+生成的手机端适配版本 |
| scene | 模特图/场景图：模特置于场景中的展示图 |
| point | 卖点图：突出商品卖点的视觉营销图 |
| ins | 种草图：种草风格展示图 |
| size | 尺码图：商品尺码信息图 |
| white | 白底图：商品精修白底主图 |

### 扣费标准

以下扣点从当前模型配置实时读取。

| 模型 | 扣费配置（点/张，经济 / 稳定） |
| --- | --- |
| GPT_2_5_IMAGE （配置默认） | 1K：low **稳** 4；medium **稳** 30；high **稳** 120；xhigh **稳** 150；max **稳** 200<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150；xhigh **稳** 240；max **稳** 280<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300；xhigh **稳** 330；max **稳** 360 |
| GPT_2_5_F_IMAGE | 1K：low **稳** 4；medium **稳** 30；high **稳** 120；xhigh **稳** 150；max **稳** 200<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150；xhigh **稳** 240；max **稳** 280<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300；xhigh **稳** 330；max **稳** 360 |
| GPT_2_IMAGE | 1K：low **稳** 4；medium **稳** 30；high **稳** 120<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300 |
| BANANA_PRO | 1K：**稳** 40<br>2K：**稳** 40<br>4K：**稳** 50 |
| BANANA_2 | 1K：**稳** 40<br>2K：**稳** 40<br>4K：**稳** 50 |
| BANANA_2_LITE | 1K：**稳** 20 |
| SEEDREAM5_PRO | 1K：**稳** 25<br>2K：**稳** 50 |
| WAN2_7 | 1K：**稳** 25<br>2K：**稳** 25 |

> 按各类素材实际生成张数累计扣点。


## brandKey嵌套字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| brandColor | String | 品牌颜色，#RRGGBB |
| fontStyle | String | 字体风格 |
| salesRegion | String | 销售地区 |
| language | String | 语言 |
| platform | String | 平台 |
| customSettings | String | 自定义描述 |

## aPlusStyles/pointStyles嵌套字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | String | 排版素材ID |
| prompt | String | 排版提示词 |

## curl示例

```bash
curl "${LINKFOX_TOOL_GATEWAY}/aigc/wearCollection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H 'Content-Type: application/json' -H 'User-Agent: LinkFox-Skill/2.0' \
  --data '{"requestId": "clothing-suite-task-001", "params": {"imageList": ["https://example.com/clothing.png"], "sellerPoint": "Breathable cotton fabric", "modelTypeNum": 1, "sellerTypeNum": 1}}'
```

以上参数仅为结构示例；必须替换为真实素材、模型和本次任务ID，不能调用示例占位地址执行收费测试。

## 错误处理

HTTP200不保证业务成功。检查error、errcode及code；无成功字段时不要继续依赖链。处理400参数错误、401/403认证或归属失败、402余额不足、404任务不存在及下游错误。模板支持网关ToolErrorResponse XML标准化。不要只依赖脚本退出码，失败响应可能仍被保存为JSON。

未配置Key、401鉴权异常或402余额不足时，读取本skill内置 [onboarding.md](onboarding.md)，按原有AIGC流程引导。403成员归属或权限失败不能通过充值解决。手机号登录、短信及套餐支付按用户选择执行，不自动操作；不将登录Token、验证码或Key写入任务产物。

## Feedback

反馈接口：https://skill-api.linkfox.com/api/v1/public/feedback 。记录路径、requestId/taskId及脱敏错误摘要；参数类型不符、异常响应结构、持续查询失败可反馈。绝不包含Key、Authorization、Base64或私密素材内容。
