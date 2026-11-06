# 商品图转视频 接口说明

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

## 接口：查询模型枚举

### 调用规范

- **请求方式**：GET，超时 5 秒。
- **请求地址**：`${LINKFOX_AI_API_URL}/image/video/model/config/list?bizType=30`。
- **基础地址**：`LINKFOX_AI_API_URL`，默认 `https://ai-api.linkfox.com`，与生成网关独立配置。
- **请求头**：`Referer: https://wiki.linkfox.com/`、`User-Agent: LinkFox-Skill/2.0`；无需认证，不发送生成密钥或会话身份头。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bizType | integer（查询参数） | 是 | 本技能固定为 `30`。 |

### 响应结构

接口返回 `code` 和 `data`：HTTP 请求成功、`code` 为 `200` 或 `"200"` 且 `data` 为数组时，查询成功。

| 字段 | 类型 | 说明 |
|---|---|---|
| data[].code | string | 模型配置标识。 |
| data[].name | string | 模型展示名称。 |
| data[].apiCode | string | 下游模型标识，按实际返回提供。 |
| data[].supportedRatios / supportedResolutions / supportedDurations / supportedQualities | array[string] / null | 支持的比例、分辨率、时长和质量档位。 |
| data[].refImageCount | integer | 模型参考图上限，仍须遵守创建接口的素材数量限制。 |
| data[].isMaintenance | boolean | 维护标记；脚本排除维护中的模型。 |

### 脚本调用

`python scripts/image_to_video_async.py --list-models --inline`

脚本返回 `source`、`models` 和完整结果路径 `dataFile`；选型使用 `models[].name`，创建参数使用 `models[].requestValue`。优先使用 `apiCode`，缺失时使用脚本已知映射；无法确定时为 `null`，须先核实，不能猜测。
查询支持 `--no-cache` 和 `--allowed-models '<JSON 数组>'`，后者仅按明确业务限制筛选模型。查询不创建任务或改写生成参数。

仅查询失败时返回 `source=fallback` 并使用本技能的静态列表，需告知用户正在使用兜底信息；查询成功但列表为空、模型缺失或处于维护状态时，不恢复静态选项。

## 接口：图转视频（imageToVideo）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/imageToVideo`

### 请求参数

#### 网关 POST Body

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| requestId | String | 否 | 可选兼容字段；提供时原样转发，缺失时不补充 |
| chatId | String | 否 | Agent 会话 ID，最长128字符 |
| messageId | String | 否 | Agent 消息 ID，最长128字符 |
| title | String | 否 | 业务展示标题 |
| params | Object | 是 | 非空业务参数对象，字段见下表；身份由认证凭证解析，不传顶层memberId |

#### params 业务参数

V3 请求体区分可选与条件必填字段，创建请求要求 params 非空，具体模型业务校验由下游执行。camera 的具体枚举、resolution 的逐模型默认值及 isPro 的详细兼容映射尚未明确；按服务端实际支持值处理，不自行假定。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.videoType | String | 是 | 模型枚举优先通过[查询模型枚举](#接口查询模型枚举)获取，使用脚本结果的 `models[].requestValue`；仅查询失败时使用下方静态列表兜底。 |
| params.videoTime | java.math.BigDecimal（JSON number） | 是 | 视频时长（秒）；具体支持值见下方各模型参数支持情况 |
| params.video | List<String> | 否 | 参考视频 URL 列表；支持模型、数量、格式及计费规则见下方参考视频|
| params.promptOptimizer | Boolean | 否 | 是否开启提示词优化；true：开启，false：不开启；默认 false |
| params.isPro | Boolean | 否 | 是否开启高质量 / Pro 模式（已废弃，建议改用 resolution）；兼容规则见下方各模型参数支持情况 |
| params.voice | Boolean | 否 | 是否生成声音；具体支持模型及限制见下方各模型参数支持情况 |
| params.lastFrameImageUrl | String | 否 | 尾帧图地址；具体支持模型及限制见下方各模型参数支持情况|
| params.camera | String | 否 | 运镜参数；具体支持模型及可选值见下方各模型参数支持情况|
| params.templateKey | String | 否 | 视频模板标识，传入后走模板模式，由服务端根据模板配置自动生成最终 prompt，无需手动传 prompt；固定可选值：product-showcase：产品展示，适合多角度展示商品外观、材质、细节；ugc-seeding：UGC种草，适合用户视角真实分享体验；pain-solution：痛点解决，适合先呈现痛点再演示产品解决方案；furniture-scene：家居场景，适合展示家具/家居用品在真实室内空间中的摆放、搭配和使用效果；注意：与 prompt 互斥，传了 templateKey 则忽略 prompt|
| params.productInfo | String | 否 | 商品信息（模板模式使用），描述商品特征用于生成更精准的视频 prompt；不传时仅使用模板默认配置；建议用 `[维度]：内容` 逐行填写；各模板关注维度：• product-showcase：展示目标、外观重点、展示点、细节路径、场景化使用、主体锚点；• ugc-seeding：口播素材、推荐点、使用动作、人物/商品锚点、适用场景；• pain-solution：痛点、问题对象、前后状态、解决动作、可观察结果、口播素材；• furniture-scene：空间类型、房间布局、家具摆放、材质色彩、搭配元素、使用动作、光线氛围、镜头重点|
| params.language | String | 否 | 目标语言（模板模式使用）；默认 英文|
| params.saleCountry | String | 否 | 销售国家/地区（模板模式使用）；默认 美国|
| params.imageUrl | String | 条件必填 | 原图地址（单图/首帧模式必传）；格式： jpg、jpeg、png、webp；happyhorse-v2 / minimax-h3-lite 不支持，其他模型的具体支持模式见下方各模型参数支持情况|
| params.imageList | List<String> | 条件必填 | 多图参考图列表；kling-v3-omni：1～7 张；kling-v2-6：1～2 张；gemini-omni-flash：1～10 张；doubao-seedance-2-5：1～30 张；wan3：1～10 张；doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / happyhorse-v2 / minimax-h3 / minimax-h3-lite：1～9 张；imageUrl 与 imageList 二选一；happyhorse-v2 / minimax-h3-lite 必须传 imageList|
| params.prompt | String | 条件必填 | 视频提示词（4000 字以内）；注意：不传 templateKey 时必须传 prompt|
| params.resolution | String | 条件必填 | 视频分辨率；具体支持值、默认值及必传规则见下方各模型参数支持情况|
| params.aspectRatio | String | 条件必填 | 视频比例；具体支持值及必传/自适应规则见下方各模型参数支持情况|

#### 接口与素材约束

- 业务字段全部放入非空 `params`，外层仅定义 requestId、chatId、messageId、title、params；不发送顶层 memberId，成员及团队由认证身份解析。普通 skill 不发送渠道头时 externalAgentPlatform 默认 skill，不伪装 workbuddy。
- 请求契约以 tools 的 feature-workbuddy-change 分支为准（外层 OpenApiImageMakeDto）。实际下游 path 为 `/image/auth/agent/imagemake/imageToVideoV3`；下游 OpenAPI 路径 `/image/v3/make/imageToVideo` 仅用于说明业务字段，不能替换本接口网关地址或增加为独立操作。
- 所有图片与视频，包括外部 HTTP(S) URL，均按 [file-upload.md](file-upload.md) 先上传，生成字段只使用返回的 viewUrl；上传失败停止，轮询不重新上传。低层创建入口不替用户上传；只有 run_task.py 的素材字段接受本地路径或外部源 URL。
- requestId 为可选兼容字段；提供时原样转发，缺失时不自动生成。同一任务使用已接受的 taskId 恢复查询；超时不自动重提。创建请求要求 params 非空，模型能力、必填条件和数量等最终由下游校验，不能凭配置默认模型省略文档要求。
- 透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 环境头。网关及主／备用密钥读取沿用公共规则，凭证不放入请求业务字段或落盘文件。

#### 各模型参数支持情况

以下静态模型列表及能力仅在查询失败时兜底，不限制查询成功时的可选范围。

以下参数从当前图转视频模型配置读取，支持的模型及能力以当前接口返回为准。

| 模型 | 分辨率 | 时长（秒） | 参考图上限 | 声音 | 尾帧 | 比例 |
| --- | --- | --- | --- | --- | --- | --- |
| minimax-h3-lite （配置默认） | 768P | 5 / 10 / 15 | 9 | 不支持 | 不支持 | 自适应 / 9:16 / 16:9 / 1:1 / 4:3 / 3:4 / 21:9 |
| wan3 | 480P / 720P / 1080P | 5 / 10 / 15 / 20 / 25 / 30 | 10 | 不支持 | 支持 | 16:9 / 4:3 / 1:1 / 3:4 / 9:16 |
| doubao-seedance-2-5 | 480P / 720P / 1080P | 5 / 10 / 15 / 20 / 25 / 30 | 30 | 支持 | 支持 | 9:16 / 16:9 / 1:1 / 4:3 / 3:4 / 21:9 |
| doubao-seedance-2-0-fast | 480P / 720P | 5 / 10 / 15 | 9 | 支持 | 支持 | 9:16 / 16:9 / 1:1 / 4:3 / 3:4 / 21:9 |
| doubao-seedance-2-0-mini | 480P / 720P | 5 / 10 / 15 | 9 | 支持 | 支持 | 9:16 / 16:9 / 1:1 / 4:3 / 3:4 / 21:9 |
| happyhorse-v2 | 720P / 1080P | 5 / 10 / 15 | 9 | 不支持 | 不支持 | 9:16 / 16:9 / 1:1 / 4:3 / 3:4 / 21:9 |
| doubao-seedance-2-0 | 480P / 720P / 1080P | 5 / 10 / 15 | 9 | 支持 | 支持 | 9:16 / 16:9 / 1:1 / 4:3 / 3:4 / 21:9 |
| gemini-omni-flash | 720P / 1080P / 4K | 5 / 10 | 10 | 不支持 | 不支持 | 16:9 / 9:16 |
| kling-v2-6 | 720P / 1080P | 5 / 10 | 2 | 支持· 仅 1080P | 支持· 仅 1080P · 无声 | 自适应 |
| minimax-h3 | 768P / 2K | 5 / 10 / 15 | 9 | 不支持 | 支持 | 16:9 / 9:16 / 1:1 / 4:3 / 3:4 / 21:9 |
| kling-v3-omni | 720P / 1080P | 5 / 10 / 15 | 7 | 不支持 | 支持· 仅 1080P · 无声 | 1:1 / 9:16 / 16:9 |

---

#### 模型展示名称

面向用户可使用以下名称；请求仍使用 `videoType` 代码。MiniMax H3 的两个代码须结合分辨率和能力表区分。

| videoType | 展示名称 |
|---|---|
| kling-v2-6 | 可灵 V2.6 |
| kling-v3-omni | 可灵 V3-Omni |
| doubao-seedance-2-0-mini | 豆包 Seedance 2.0 Mini |
| doubao-seedance-2-5 | 豆包 Seedance 2.5 |
| gemini-omni-flash | Omni Flash 1.1 |
| minimax-h3 | MiniMax H3 |
| minimax-h3-lite | MiniMax H3（768P 多图模式） |

#### 参考视频

##### OpenAPI V3 参数边界

本接口使用 `imageList` 传参考图片，使用 `video` 传参考视频。`video` 是 URL 数组，当前公开契约最多支持 1 段参考视频。

| 素材类型 | OpenAPI 参数 | 支持模型 | 数量与主要限制 |
| --- | --- | --- | --- |
| 参考图片 | `imageList` | 见上方请求参数中的 `params.imageList` | 数量上限由模型配置决定 |
| 参考视频 | `video` | doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / doubao-seedance-2-5 / WAN3 | 最多 1 段，支持 mp4 / mov |

##### 参考视频限制

| 模型 | 时长 | 文件大小 | 编码 / 画面限制 |
| --- | --- | --- | --- |
| doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini | 1～15 秒 | 最大 200 MB | H.264/AVC 或 H.265/HEVC；24～60 FPS；单边 300～6000 像素；宽高比 0.4～2.5 |
| doubao-seedance-2-5 | 1～30 秒 | 最大 200 MB | H.264/AVC 或 H.265/HEVC；24～60 FPS；单边 300～6000 像素；宽高比 0.4～2.5 |
| WAN3 | 1～15 秒 | 最大 100 MB | 单边 240～4096 像素；宽高比 1:8～8:1；参考视频时长与输出时长之和不超过 30 秒 |

运行时以目标环境已发布的 `biz_type=30` 模型配置为准；模型未开放参考视频能力时，提交 `video` 可能创建失败或不生效。

##### 参考视频计费规则

- 当 `video` 传入有效参考视频时，`doubao-seedance-2-0`、`doubao-seedance-2-0-fast`、`doubao-seedance-2-0-mini`、`doubao-seedance-2-5` 和 `WAN3` 的基础扣点按 **2 倍**计算。
- 基础扣点仍按目标模型已发布配置中的 `resolution` 和 `videoTime` 计算，再乘以参考视频倍率；不传参考视频时不加倍。
- 当前最多支持 1 段参考视频，传入空数组或空白 URL 不计为参考视频。

##### 素材组合规则

- 参考视频用于补充动作、运镜和节奏，不替代图转视频的商品图片；通常应传 `imageUrl` 或 `imageList`。
- `imageUrl` 与 `imageList` 只能选择一种；使用多张参考图片时传 `imageList`。
- `video` 可与 `imageUrl` 或 `imageList` 一起使用；不要同时传 `lastFrameImageUrl`，参考素材模式与首尾帧模式互斥，WAN3 会以参考素材模式为准并移除首尾帧输入。
- 提示词中直接用自然语言描述如何参考视频，例如“参考视频的镜头节奏和动作”；参考视频使用公开字段 `video`，不要传内部字段 `referenceVideo`。
- 参考视频 URL 必须在任务处理期间保持可访问，建议使用稳定的 HTTPS 地址。

#### 完整流程 CLI 与运行约定

完整工作流由 `../scripts/run_task.py` 编排。以下是本地 CLI，非接口请求字段。

| 参数／选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| parameters | JSON string | 创建时与 --params-file 二选一 | 参数对象；`-` 表示从 stdin 读取；业务字段嵌套于 params。 |
| --params-file | path | 否 | UTF-8 JSON 文件，与位置参数互斥。 |
| --task-id | string | 续查时是 | 已接受任务编号；禁止同时传创建参数，不上传或创建。 |
| --member-id | string | 否 | 只加入 taskQuery，不能据此改变任务归属。 |
| --timeout | number | 否 | 秒，必须大于 0；视频默认 1200（20 分钟），保留图像分支默认 600（10 分钟）。 |
| --poll-interval | number | 否 | 秒，不得负数；视频默认 10；图像分支 5～10 秒。 |
| --initial-delay | number | 否 | 秒，不得负数；新视频默认 120，续查默认 0；图像分支默认 10。 |

- requestId 仅在提供时原样转发，缺失时不补充；素材在本次运行中按来源去重，多图保留顺序，映射不视为可跨任务复用的永久缓存。
- 低层 `image_to_video_async.py '<JSON>' [--inline] [--no-cache]` 保留 24h 缓存：路径为 `<cwd>/linkfox/.cache/linkfox-aigc-image-to-video/`，按请求 JSON 排序后的 SHA256 前 16 位取键；兼容既有缓存格式并缓存错误结果，避免同参自动重试；已解析但不是对象的缓存转为错误响应并保留原值，不当作未命中重新请求。`--no-cache` 关闭这一层。封装调用 call_api.run 始终传 --no-cache，未叠加第二层缓存。
- transportHttpStatus 供编排判断真实外层状态。缓存未保存状态时不伪造；不自动重提创建。需要核对现有任务或人工明确新的生成后再按成本约束处理。
- 所有业务入口在请求前检查 cwd/linkfox 可写；ACPX_WORKSPACES 为空或首路径等于 cwd，冲突时先取消该配置。禁止回退 home/tmp；Windows 使用 PYTHONUTF8=1 或 `python -X utf8`。
- API 完整 JSON 写入会话 data，默认大于 8000 字节仅摘要，--inline 强制全量打印并仍保存。run_task.py 不支持 --inline，额外下载媒体至 media，并保存资产清单；原始终态 JSON 和清单均保留，创建零费用不覆盖查询费用。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 网关创建成功返回的任务编号，表示接受任务，不表示完成。 |
| costToken | integer / string | 创建通常为 0，不代表免费；若有 X-Cost-Token 响应头则以响应头覆盖。 |
| errcode | integer / string / null | 网关业务状态，按公共基础规则判断；网关 XML ToolErrorResponse 转成此字段。 |
| errmsg | string | 网关消息或错误原因。 |
| code | integer / string / null | 如返回则保留原业务代码，异常时不得继续依赖链。 |
| error | string | 连接失败、无效响应或接口业务错误；出现时停止依赖链。 |
| details | string | 非 JSON/XML 响应的原始错误内容，如返回则保留。 |
| costCredit | integer / string | 脚本从 X-Cost-Credit 响应头保留的实际费用，缺失表示未知。 |
| transportHttpStatus | integer / null | 业务封装保存的真实外层 HTTP 状态；连接失败为 null，已有缓存可能未保存该字段。 |
| _cache.hit | boolean | 本地命中 24h 响应缓存时为 true，不是服务端字段。 |
### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 只有创建响应正常且返回 taskId 时才开始查询；脚本退出码本身不能证明成功，失败响应也会落盘。非对象 JSON 响应转为 error 与保留原文的 details，停止依赖链，不因解析失败自动重新提交。
- HTTP 400 参数错误按本接口字段、模型限制及错误消息处理；403 归属／权限问题不充值。认证或用量问题按 onboarding.md 处理，停止当前生成链路。
- 网关契约使用 taskId 与查询状态，不使用下游的 `data.id`、数字状态或 `count` 封装。新建超时、失败或结果不确定时不自动重建任务。

#### 模型与模板补充约定

- kling-v3-omni 多图模式必须传 aspectRatio，支持 `1:1`、`16:9`、`9:16`；首尾帧模式仅自适应，不传该参数。参数错误时保留服务端列出的支持值，不自动换模型试探。
- 模板生成的 prompt 为通用文本，所有 videoType 均可配合模板；推荐 doubao-seedance-2-0、kling-v3-omni、happyhorse-v2。推荐不改变模型支持表中的限制。
- 任务失败时按实际错误核对提示词、上传素材可访问性及套餐算力；结果为空或超时，保留 taskId，用 --task-id 续查并按需调整 --timeout，不重新生成。

#### 算力与下游计费配置

生成按模型、分辨率和视频时长动态扣点；配置见下表，参考视频倍率另行计算。表格用于估算，当前扣费以服务端配置和实际扣除为准。

| 模型 | 扣费配置（点） |
| --- | --- |
| minimax-h3-lite （配置默认） | 768P：5秒 **15**；10秒 **30**；15秒 **45** |
| wan3 | 480P：5秒 **90**；10秒 **180**；15秒 **270**；20秒 **360**；25秒 **450**；30秒 **540**<br>720P：5秒 **175**；10秒 **350**；15秒 **525**；20秒 **700**；25秒 **875**；30秒 **1050**<br>1080P：5秒 **355**；10秒 **710**；15秒 **1065**；20秒 **1420**；25秒 **1775**；30秒 **2130** |
| doubao-seedance-2-5 | 480P：支持有声；5秒 **265**；10秒 **530**；15秒 **795**；20秒 **1060**；25秒 **1325**；30秒 **1590**<br>720P：支持有声；5秒 **595**；10秒 **1190**；15秒 **1785**；20秒 **2380**；25秒 **2975**；30秒 **3570**<br>1080P：支持有声；5秒 **1620**；10秒 **3240**；15秒 **4860**；20秒 **6480**；25秒 **8100**；30秒 **9720** |
| doubao-seedance-2-0-fast | 480P：支持有声；5秒 **105**；10秒 **210**；15秒 **315**<br>720P：支持有声；5秒 **215**；10秒 **430**；15秒 **645** |
| doubao-seedance-2-0-mini | 480P：支持有声；5秒 **35**；10秒 **70**；15秒 **105**<br>720P：支持有声；5秒 **70**；10秒 **140**；15秒 **210** |
| happyhorse-v2 | 720P：5秒 **185**；10秒 **370**；15秒 **555**<br>1080P：5秒 **240**；10秒 **480**；15秒 **720** |
| doubao-seedance-2-0 | 480P：支持有声；5秒 **200**；10秒 **400**；15秒 **600**<br>720P：支持有声；5秒 **400**；10秒 **800**；15秒 **1200**<br>1080P：支持有声；5秒 **1500**；10秒 **3000**；15秒 **4500** |
| gemini-omni-flash | 720P：5秒 **165**；10秒 **330**<br>1080P：5秒 **245**；10秒 **490**<br>4K：5秒 **490**；10秒 **980**<br>360P：5秒 **50**；10秒 **100** |
| kling-v2-6 | 720P：有声<br>1080P：有声；5秒 **400**；10秒 **800**；15秒 **800**<br>720P：5秒 **200**；10秒 **400**；15秒 **400**<br>1080P：5秒 **300**；10秒 **500**；15秒 **500** |
| minimax-h3 | 768P：5秒 **200**；10秒 **400**；15秒 **600**<br>2K：5秒 **320**；10秒 **640**；15秒 **960** |
| kling-v3-omni | 720P：5秒 **300**；10秒 **600**；15秒 **900**<br>1080P：5秒 **400**；10秒 **800**；15秒 **1200** |

> 按模型、分辨率和视频时长扣点；传入参考视频时的倍率规则见上方[参考视频](#参考视频)。


计费表中的 360P 或部分 15 秒配置不代表模型支持这些参数；是否可用仍以参数支持表与服务端配置为准。费用仍由下游处理，count 按 2000 倍换算；不是额外的网关响应字段或可据此承诺的收费额。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/imageToVideo" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"params":{"videoType":"doubao-seedance-2-5","videoTime":5,"imageList":["https://uploaded.example/product.png"],"templateKey":"product-showcase","productInfo":"便携水瓶","resolution":"720p","aspectRatio":"16:9"}}'
```

示例地址必须替换为本次上传返回的 viewUrl；不得用占位任务或素材执行收费测试。

## 接口：查询任务（taskQuery）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/taskQuery`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| taskId | string | 是 | 已接受的当前或既有图像／视频任务编号。 |
| memberId | string | 否 | 兼容既有任务的成员标识，不能绕过认证身份或归属校验。 |

#### 查询限制与 CLI

- 使用 `../scripts/query_task.py '<JSON>' [--inline] [--no-cache]`；脚本始终关闭缓存，即使未显式传 --no-cache 也不读写响应缓存。
- 公共 taskQuery 同时服务本次创建与既有图像／视频任务；本分支不存在 makeTaskQuery，不推导新的查询端点。
- 此接口不接受 format 或 containsSyntheticPerformer 等生成／扩展参数。视频查询至少间隔 10 秒；完整视频任务默认首次等待 120 秒，总等待 20 分钟，超时仅续查原任务。
- 透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。只读状态不代表免费生成；按实际返回费用记录，缺失时为未知。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 任务编号。 |
| status | string | PROCESSING：处理中；SUCCESS：成功；FAILED：失败。 |
| resultList | array<object> | 结果项列表，字段见下表。 |
| errorMsg | string | 任务级错误消息，如有则保留。 |
| costToken | integer / string | 任务查询报告的实际费用；X-Cost-Token 响应头优先，不能被创建时的 0 覆盖。 |
| errcode | integer / string / null | 网关业务状态，按公共基础规则判断；网关 XML ToolErrorResponse 转成此字段。 |
| errmsg | string | 网关消息或错误原因。 |
| code | integer / string / null | 如返回则保留原业务代码，异常时不得继续依赖链。 |
| error | string | 连接失败、无效响应或接口业务错误；出现时停止依赖链。 |
| details | string | 非 JSON/XML 响应的原始错误内容，如返回则保留。 |
| costCredit | integer / string | 脚本从 X-Cost-Credit 响应头保留的实际费用，缺失表示未知。 |
| transportHttpStatus | integer / null | 业务封装保存的真实外层 HTTP 状态；连接失败为 null，已有缓存可能未保存该字段。 |
| _cache.hit | boolean | 兼容已保存响应中的缓存标记；当前查询入口禁用缓存，不产生缓存命中。 |

#### resultList[]

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 结果资源标识。 |
| url | string | 成功资源的下载 URL。 |
| type | string / number | 透传下游 extendField.type；取值为实际返回的字符串或数字，不限定固定枚举。 |

当前网关不返回单项 status/errorCode/errorMsg、width/height/format/size、完整 extendField 或 containsSyntheticPerformer，不推断这些信息。下游数字状态 `data.status=3/4` 分别表示成功／失败；网关使用 SUCCESS／FAILED 判断，`data.id` 不能替代 taskId。

#### 本地下载清单

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 原查询任务编号。 |
| status | string | 原查询任务状态。 |
| costToken | integer / string / null | 查询实际算力费用，缺失为 null；不从创建结果补零。 |
| costCredit | integer / string / null | 查询实际费用响应头值，缺失为 null；不从创建结果补零。 |
| items | array<object> | 每项保留 id、type。若已保存的查询 JSON 中确实有 status/errorCode/errorMsg 则原样保留，不补造。 |
| items[].id | string / null | 原结果资源标识；缺失不补造。 |
| items[].type | string / number / null | 原结果资源类型；缺失不补造。 |
| items[].status | 原值 | 仅输入查询 JSON 实际包含此字段时保留。 |
| items[].errorCode | 原值 | 仅输入查询 JSON 实际包含此字段时保留。 |
| items[].errorMsg | 原值 | 仅输入查询 JSON 实际包含此字段时保留。 |
| items[].localPath | string | 成功下载的本地绝对路径。 |
| items[].downloadError | string | 下载失败或跳过原因，包括缺少有效 URL、结果项格式异常及兼容结果项未成功；只重试下载，不重新生成。 |
| mediaPaths | array<string> | 成功文件路径列表； stdout 同时用 Saved full response: [路径数组] 输出。 |

媒体下载按结果 URL／Content-Type 识别扩展名，记录资源 ID 和类型；保留非空文件，失败清理临时下载文件。`../scripts/download_results.py <终态JSON>` 只接受响应正常且状态为 SUCCESS 的查询 JSON，读取原查询并重试下载，不请求 LinkFox 或创建任务。媒体文件和清单写入同一会话 media/data。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- PROCESSING 继续原任务查询；SUCCESS 进入媒体下载；FAILED 保留错误并停止，不自动重建或换模型。
- 未知状态、无效响应或查询错误时停止，保留 taskId 与原始响应；403 权限／归属错误不能靠充值解决，404 表示任务不存在。
- SUCCESS 下的媒体下载失败仅重试下载；没有可用媒体时说明现状，不把空文件、JSON 或未返回属性当作成品。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/taskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"taskId":"已接受的任务编号"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-image-to-video",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
