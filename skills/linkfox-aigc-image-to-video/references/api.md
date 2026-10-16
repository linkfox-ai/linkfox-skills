# 图转视频 API 参考

## 调用规范

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/aigc/imageToVideo`，网关未配置时回退正式网关。
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
| params.videoType | String | 是 | 模型类型；具体支持值见下方各模型参数支持情况|
| params.videoTime | java.math.BigDecimal | 是 | 视频时长（秒）；具体支持值见下方各模型参数支持情况 |
| params.video | List<String> | 否或条件必填 | 参考视频 URL 列表；支持模型、数量、格式及计费规则见下方参考视频|
| params.promptOptimizer | Boolean | 否或条件必填 | 是否开启提示词优化；true：开启，false：不开启；默认 false |
| params.isPro | Boolean | 否或条件必填 | 是否开启高质量 / Pro 模式（已废弃，建议改用 resolution）；兼容规则见下方各模型参数支持情况 |
| params.voice | Boolean | 否或条件必填 | 是否生成声音；具体支持模型及限制见下方各模型参数支持情况 |
| params.lastFrameImageUrl | String | 否或条件必填 | 尾帧图地址；具体支持模型及限制见下方各模型参数支持情况|
| params.camera | String | 否或条件必填 | 运镜参数；具体支持模型及可选值见下方各模型参数支持情况|
| params.templateKey | String | 否或条件必填 | 视频模板标识，传入后走模板模式，由服务端根据模板配置自动生成最终 prompt，无需手动传 prompt；固定可选值：；product-showcase：产品展示，适合多角度展示商品外观、材质、细节；ugc-seeding：UGC种草，适合用户视角真实分享体验；pain-solution：痛点解决，适合先呈现痛点再演示产品解决方案；furniture-scene：家居场景，适合展示家具/家居用品在真实室内空间中的摆放、搭配和使用效果；注意：与 prompt 互斥，传了 templateKey 则忽略 prompt|
| params.productInfo | String | 否或条件必填 | 商品信息（模板模式使用），描述商品特征用于生成更精准的视频 prompt；各模板关注维度：；• product-showcase：展示目标、外观重点、展示点、细节路径、场景化使用、主体锚点；• ugc-seeding：口播素材、推荐点、使用动作、人物/商品锚点、适用场景；• pain-solution：痛点、问题对象、前后状态、解决动作、可观察结果、口播素材；• furniture-scene：空间类型、房间布局、家具摆放、材质色彩、搭配元素、使用动作、光线氛围、镜头重点|
| params.language | String | 否或条件必填 | 目标语言（模板模式使用）；默认 英文|
| params.saleCountry | String | 否或条件必填 | 销售国家/地区（模板模式使用）；默认 美国|
| params.imageUrl | String | 否或条件必填 | 原图地址（单图/首帧模式必传）；格式： jpg、jpeg、png、webp；happyhorse-v2 / minimax-h3-lite 不支持，其他模型的具体支持模式见下方各模型参数支持情况|
| params.imageList | List<String> | 否或条件必填 | 多图参考图列表；kling-v3-omni：1～7 张；kling-v2-6：1～2 张；gemini-omni-flash：1～10 张；doubao-seedance-2-5：1～30 张；wan3：1～10 张；doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / happyhorse-v2 / minimax-h3 / minimax-h3-lite：1～9 张；imageUrl 与 imageList 二选一；happyhorse-v2 / minimax-h3-lite 必须传 imageList|
| params.prompt | String | 否或条件必填 | 视频提示词（4000 字以内）；注意：不传 templateKey 时必须传 prompt|
| params.resolution | String | 否或条件必填 | 视频分辨率；具体支持值、默认值及必传规则见下方各模型参数支持情况|
| params.aspectRatio | String | 否或条件必填 | 视频比例；具体支持值及必传/自适应规则见下方各模型参数支持情况|

## 公共任务上下文

请求外层只定义requestId、chatId、messageId、title、params。业务参数必须放params；成员和团队由服务端根据认证身份解析，不能靠memberId字段指定。chatId/messageId最长128字符。普通skill不发送渠道头时externalAgentPlatform默认skill；不要自行伪装workbuddy。

本分支实际下游创建路径：`/image/auth/agent/imagemake/imageToVideoV3`。下方V3/V4文档仅说明params业务能力，不能据此更换实际调用路径。

## 响应与查询

创建返回taskId及costToken=0，0不代表免费。使用本目录scripts/query_task.py调用 `/aigc/taskQuery`，请求taskId及可选memberId，每次使用--no-cache。该查询也服务原有图像/视频任务，不存在本分支专属的makeTaskQuery接口。

查询响应字段：taskId、status（PROCESSING/SUCCESS/FAILED）、resultList、errorMsg、costToken。结果项仅定义id、url、type；type取自下游extendField.type。当前后端不返回单项status/errorCode/errorMsg、width/height/format/size、完整extendField或containsSyntheticPerformer；skill不得推断未返回的信息，也不能通过查询传format或containsSyntheticPerformer。

费用仍由下游处理，count按2000倍换算。官方脚本保留响应头X-Cost-Token/X-Cost-Credit提供的实际费用，不使用创建时的0覆盖查询费用。没有费用时表示未知。

## 素材准备

本地图片或视频读取并按内置 [file-upload.md](file-upload.md)执行上传。外部URL也必须先下载上传，生成接口只使用上传返回的viewUrl。仅处理本次接口实际需要的素材：视频翻译不要求额外上传图片，视频编辑的参考图片可选。

## 下游业务字段及模型参考

以下为已下载的业务文档，仅作为字段、模型限制及业务条件参考。其中下游id/status/count/响应封装不能替代上方网关taskId/status/costToken契约；文档里的单项扩展字段当前未由网关结果VO透出。

# 图转视频 V3

根据图片和可选参考视频生成 AI 视频，支持多种模型、时长和风格控制。

**下游 POST** `/image/v3/make/imageToVideo`  
Content-Type: `application/json`

### 请求体

| 参数 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| videoType | string | 必填 | 模型类型；具体支持值见下方[各模型参数支持情况](#各模型参数支持情况) |
| videoTime | number | 必填 | 视频时长（秒）；具体支持值见下方[各模型参数支持情况](#各模型参数支持情况) |
| video | array[string] | 可选 | 参考视频 URL 列表；支持模型、数量、格式及计费规则见下方[参考视频](#参考视频) |
| promptOptimizer | boolean | 可选 | 是否开启提示词优化；`true`：开启，`false`：不开启；默认 false |
| isPro | boolean | 可选 | 是否开启高质量 / Pro 模式（已废弃，建议改用 `resolution`）；兼容规则见下方[各模型参数支持情况](#各模型参数支持情况) |
| voice | boolean | 可选 | 是否生成声音；具体支持模型及限制见下方[各模型参数支持情况](#各模型参数支持情况) |
| lastFrameImageUrl | string | 可选 | 尾帧图地址；具体支持模型及限制见下方[各模型参数支持情况](#各模型参数支持情况) |
| camera | string | 可选 | 运镜参数；具体支持模型及可选值见下方[各模型参数支持情况](#各模型参数支持情况) |
| templateKey | string | 可选 | 视频模板标识，传入后走模板模式，由服务端根据模板配置自动生成最终 prompt，无需手动传 `prompt`<br>**固定可选值**：<br>`product-showcase`：产品展示，适合多角度展示商品外观、材质、细节<br>`ugc-seeding`：UGC种草，适合用户视角真实分享体验<br>`pain-solution`：痛点解决，适合先呈现痛点再演示产品解决方案<br>`furniture-scene`：家居场景，适合展示家具/家居用品在真实室内空间中的摆放、搭配和使用效果<br>注意：与 `prompt` 互斥，传了 `templateKey` 则忽略 `prompt` |
| productInfo | string | 可选 | 商品信息（模板模式使用），描述商品特征用于生成更精准的视频 prompt<br>各模板关注维度：<br>• `product-showcase`：展示目标、外观重点、展示点、细节路径、场景化使用、主体锚点<br>• `ugc-seeding`：口播素材、推荐点、使用动作、人物/商品锚点、适用场景<br>• `pain-solution`：痛点、问题对象、前后状态、解决动作、可观察结果、口播素材<br>• `furniture-scene`：空间类型、房间布局、家具摆放、材质色彩、搭配元素、使用动作、光线氛围、镜头重点 |
| language | string | 可选 | 目标语言（模板模式使用）；默认 英文 |
| saleCountry | string | 可选 | 销售国家/地区（模板模式使用）；默认 美国 |
| imageUrl | string | 条件必填 | 原图地址（单图/首帧模式必传）；格式： jpg、jpeg、png、webp；happyhorse-v2 / minimax-h3-lite 不支持，其他模型的具体支持模式见下方[各模型参数支持情况](#各模型参数支持情况) |
| imageList | array[string] | 条件必填 | 多图参考图列表；kling-v3-omni：1～7 张；kling-v2-6：1～2 张；gemini-omni-flash：1～10 张；doubao-seedance-2-5：1～30 张；wan3：1～10 张；doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / happyhorse-v2 / minimax-h3 / minimax-h3-lite：1～9 张<br>`imageUrl` 与 `imageList` 二选一；happyhorse-v2 / minimax-h3-lite 必须传 `imageList` |
| prompt | string | 条件必填 | 视频提示词（4000 字以内）；注意：不传 `templateKey` 时必须传 `prompt` |
| resolution | string | 条件必填 | 视频分辨率；具体支持值、默认值及必传规则见下方[各模型参数支持情况](#各模型参数支持情况) |
| aspectRatio | string | 条件必填 | 视频比例；具体支持值及必传/自适应规则见下方[各模型参数支持情况](#各模型参数支持情况) |

---

### 各模型参数支持情况

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

### 参考视频

#### OpenAPI V3 参数边界

本接口使用 `imageList` 传参考图片，使用 `video` 传参考视频。`video` 是 URL 数组，当前公开契约最多支持 1 段参考视频。

| 素材类型 | OpenAPI 参数 | 支持模型 | 数量与主要限制 |
| --- | --- | --- | --- |
| 参考图片 | `imageList` | 见上方[请求体](#请求体)中的 `imageList` | 数量上限由模型配置决定 |
| 参考视频 | `video` | doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / doubao-seedance-2-5 / WAN3 | 最多 1 段，支持 mp4 / mov |

#### 参考视频限制

| 模型 | 时长 | 文件大小 | 编码 / 画面限制 |
| --- | --- | --- | --- |
| doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini | 1～15 秒 | 最大 200 MB | H.264/AVC 或 H.265/HEVC；24～60 FPS；单边 300～6000 像素；宽高比 0.4～2.5 |
| doubao-seedance-2-5 | 1～30 秒 | 最大 200 MB | H.264/AVC 或 H.265/HEVC；24～60 FPS；单边 300～6000 像素；宽高比 0.4～2.5 |
| WAN3 | 1～15 秒 | 最大 100 MB | 单边 240～4096 像素；宽高比 1:8～8:1；参考视频时长与输出时长之和不超过 30 秒 |

运行时以目标环境已发布的 `biz_type=30` 模型配置为准；模型未开放参考视频能力时，提交 `video` 可能创建失败或不生效。

#### 参考视频计费规则

- 当 `video` 传入有效参考视频时，`doubao-seedance-2-0`、`doubao-seedance-2-0-fast`、`doubao-seedance-2-0-mini`、`doubao-seedance-2-5` 和 `WAN3` 的基础扣点按 **2 倍**计算。
- 基础扣点仍按目标模型已发布配置中的 `resolution` 和 `videoTime` 计算，再乘以参考视频倍率；不传参考视频时不加倍。
- 当前最多支持 1 段参考视频，传入空数组或空白 URL 不计为参考视频。

#### 素材组合规则

- 参考视频用于补充动作、运镜和节奏，不替代图转视频的商品图片；通常应传 `imageUrl` 或 `imageList`。
- `imageUrl` 与 `imageList` 只能选择一种；使用多张参考图片时传 `imageList`。
- `video` 可与 `imageUrl` 或 `imageList` 一起使用；不要同时传 `lastFrameImageUrl`，参考素材模式与首尾帧模式互斥，WAN3 会以参考素材模式为准并移除首尾帧输入。
- 提示词中直接用自然语言描述如何参考视频，例如“参考视频的镜头节奏和动作”；参考视频使用公开字段 `video`，不要传内部字段 `referenceVideo`。
- 参考视频 URL 必须在任务处理期间保持可访问，建议使用稳定的 HTTPS 地址。

#### 参考视频请求示例

```json
{
  "imageList": [
    "https://example.com/product-main.jpg",
    "https://example.com/product-detail.jpg"
  ],
  "video": [
    "https://example.com/reference.mp4"
  ],
  "videoType": "doubao-seedance-2-5",
  "videoTime": 15,
  "prompt": "保持商品主体一致，参考视频的运镜节奏和动作展示商品细节",
  "resolution": "720p",
  "aspectRatio": "9:16"
}
```

---

### 请求示例

**kling-v2-6**

**示例 1**：kling-v2-6（可灵 V2.6）— 单图首帧 + 1080p + 声音

```json
{
  "imageUrl": "https://example.com/image.jpeg",
  "videoType": "kling-v2-6",
  "videoTime": 10,
  "prompt": "商品展示视频",
  "resolution": "1080p",
  "voice": true
}
```

**示例 2**：kling-v2-6（可灵 V2.6）— 多图模式 10 秒

```json
{
  "imageList": [
    "https://example.com/image1.jpeg",
    "https://example.com/image2.jpeg"
  ],
  "videoType": "kling-v2-6",
  "videoTime": 10,
  "prompt": "一只白色比熊穿着红色花棉袄",
  "resolution": "720p"
}
```

**wan3**

**示例 3**：wan3 — 5 秒短视频

```json
{
  "imageUrl": "https://example.com/image.jpeg",
  "videoType": "wan3",
  "videoTime": 5,
  "prompt": "商品展示视频",
  "resolution": "720P"
}
```

**happyhorse-v2**

**示例 4**：happyhorse-v2 — 多图参考生视频

```json
{
  "imageList": [
    "https://example.com/product1.jpg",
    "https://example.com/product2.jpg",
    "https://example.com/product3.jpg"
  ],
  "videoType": "happyhorse-v2",
  "videoTime": 10,
  "prompt": "商品展示视频",
  "resolution": "1080p",
  "aspectRatio": "16:9"
}
```

**doubao-seedance-2-0-mini**

**示例 5**：doubao-seedance-2-0-mini（豆包 Seedance 2.0 Mini）— 多图模式

```json
{
  "imageList": [
    "https://example.com/product1.jpg",
    "https://example.com/product2.jpg"
  ],
  "videoType": "doubao-seedance-2-0-mini",
  "videoTime": 10,
  "prompt": "商品展示视频",
  "aspectRatio": "9:16",
  "resolution": "720p"
}
```

**kling-v3-omni**

**示例 6**：kling-v3-omni（可灵 V3-Omni）— 首尾帧模式

```json
{
  "imageUrl": "https://example.com/first-frame.jpg",
  "lastFrameImageUrl": "https://example.com/last-frame.jpg",
  "videoType": "kling-v3-omni",
  "videoTime": 10,
  "prompt": "商品从展示台缓缓旋转",
  "resolution": "1080p"
}
```

**示例 7**：kling-v3-omni（可灵 V3-Omni）— 多图参考图模式

```json
{
  "imageList": [
    "https://example.com/product1.jpg",
    "https://example.com/product2.jpg",
    "https://example.com/product3.jpg"
  ],
  "videoType": "kling-v3-omni",
  "videoTime": 10,
  "prompt": "商品多角度展示",
  "aspectRatio": "16:9",
  "resolution": "720p"
}
```

**doubao-seedance-2-0**

**示例 8**：模板模式 — 产品展示模板 + doubao-seedance-2-0 多图

```json
{
  "imageList": [
    "https://example.com/product1.jpg",
    "https://example.com/product2.jpg",
    "https://example.com/product3.jpg"
  ],
  "videoType": "doubao-seedance-2-0",
  "videoTime": 10,
  "resolution": "720p",
  "aspectRatio": "16:9",
  "templateKey": "product-showcase",
  "productInfo": "[展示目标]：展示无线蓝牙耳机的时尚外观和佩戴效果\n[外观重点]：磨砂质感充电仓和金属LOGO\n[展示点]：耳机从充电仓取出→佩戴→触控操作\n[细节路径]：耳塞硅胶套特写→充电仓磁吸开合→LED指示灯\n[场景化使用]：通勤地铁上使用\n[主体锚点]：耳机主体居中",
  "language": "中文",
  "saleCountry": "中国"
}
```

**doubao-seedance-2-5**

**示例 9**：doubao-seedance-2-5（豆包 Seedance 2.5）— 30 秒长视频 + 多图

```json
{
  "imageList": [
    "https://example.com/product1.jpg",
    "https://example.com/product2.jpg",
    "https://example.com/product3.jpg"
  ],
  "videoType": "doubao-seedance-2-5",
  "videoTime": 30,
  "prompt": "详细展示商品的各个细节和使用场景",
  "aspectRatio": "16:9",
  "resolution": "720p",
  "voice": true
}
```

**minimax-h3**

**示例 10**：minimax-h3（MiniMax H3）— 2K 高清 + 首尾帧

```json
{
  "imageUrl": "https://example.com/first-frame.jpg",
  "lastFrameImageUrl": "https://example.com/last-frame.jpg",
  "videoType": "minimax-h3",
  "videoTime": 10,
  "prompt": "商品从静态到动态的转场效果",
  "aspectRatio": "16:9",
  "resolution": "2k"
}
```

**minimax-h3-lite**

**示例 11**：minimax-h3-lite（管理台名称：MiniMax H3）— 768P 多图模式

```json
{
  "imageList": [
    "https://example.com/product1.jpg",
    "https://example.com/product2.jpg"
  ],
  "videoType": "minimax-h3-lite",
  "videoTime": 10,
  "prompt": "保持商品主体一致，生成自然的商品展示视频",
  "resolution": "768P",
  "aspectRatio": "16:9"
}
```

**gemini-omni-flash**

**示例 12**：gemini-omni-flash（Omni Flash 1.1）— 1080P 10 秒竖版

```json
{
  "imageUrl": "https://example.com/image.jpeg",
  "videoType": "gemini-omni-flash",
  "videoTime": 10,
  "prompt": "电影质感商品展示",
  "resolution": "1080P",
  "aspectRatio": "9:16"
}
```

---

### 提交后返回什么

提交成功后返回任务编号 `data.id`，表示任务已创建，结果还需等待生成。请保存编号。查看返回示例（辅助接口不在本skill范围）。

### 查询生成结果

用任务编号 `data.id` 调用获取作图结果（辅助接口不在本skill范围），每次查询至少间隔 10 秒。`data.status=3` 表示成功；若生成了图片或视频，从 `data.resultList[].url` 获取地址。`data.status=4` 表示失败。查看统一示例（辅助接口不在本skill范围）。

### 常见问题

- **报参数错误**：检查 `videoType` 是否为支持值，`videoTime` 是否匹配该类型的可选时长；happyhorse-v2 必须传 `imageList` 而非 `imageUrl`；kling-v3-omni 多图模式必须传 `aspectRatio`。V3版本会返回详细的错误提示，包括当前模型支持的所有可选值。
- **doubao-seedance-2-0-fast / doubao-seedance-2-0-mini 报分辨率错误**：两者均不支持 `1080p`，请传 `480p` 或 `720p`。
- **kling-v3-omni 报尾帧错误**：kling-v3-omni 仅 1080P 支持尾帧。
- **kling-v3-omni 报比例错误**：kling-v3-omni 多图模式必传 `aspectRatio`，可选值为 `1:1`、`16:9`、`9:16`；首尾帧模式仅支持自适应，不传此参数。
- **gemini-omni-flash 报比例或分辨率错误**：Omni Flash 1.1 仅支持 `16:9 / 9:16`，分辨率仅 `720P / 1080P / 4K`，时长仅 5 / 10 秒。参考图最多 10 张，超过会报「最多支持 10 张」。
- **任务失败**：检查提示词是否违规、图片地址是否可访问、套餐算力是否充足。
- **结果为空或超时**：延长轮询时间，复杂内容通常生成耗时更长。
- **参考视频报错**：检查 `video` 是否为 URL 数组且只包含 1 段视频，并确认当前模型支持参考视频；同时检查视频格式、大小、时长、编码、画面尺寸和 URL 可访问性。
- **参考视频扣点怎么算？**：上述支持参考视频的 Seedance 系列和 WAN3，在传入有效 `video` 时按基础扣点的 2 倍计算；基础扣点由模型配置中的分辨率和时长决定。
- **参考素材模式冲突**：`video` 可以与 `imageUrl` 或 `imageList` 一起使用，但不要同时传 `lastFrameImageUrl`；参考素材模式与首尾帧模式互斥。
- **模板模式和 prompt 能同时传吗？**：不能，`templateKey` 和 `prompt` 互斥。传入 `templateKey` 后服务端会自动生成最终 prompt，手动传的 `prompt` 会被忽略；不传 `templateKey` 时则必须传 `prompt`。
- **productInfo 怎么填？**：非必填，不传时服务端仅基于模板默认配置生成 prompt；传入后可获得更精准的个性化商品视频描述。建议用 `[维度]：内容` 格式逐行填写。
- **模板模式支持哪些模型？**：模板生成的 prompt 为通用文本，所有 `videoType` 均可配合模板模式使用，推荐 doubao-seedance-2-0 / kling-v3-omni / happyhorse-v2 出视频效果更佳。当前模板包括 `product-showcase`、`ugc-seeding`、`pain-solution` 和 `furniture-scene`。

### 扣费标准

以下扣点从当前模型配置实时读取。

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

> 按模型、分辨率和视频时长扣点；传入参考视频时的倍率规则见下方[参考视频](#参考视频)。


## curl示例

```bash
curl "${LINKFOX_TOOL_GATEWAY}/aigc/imageToVideo" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H 'Content-Type: application/json' -H 'User-Agent: LinkFox-Skill/2.0' \
  --data '{"requestId": "image-video-task-001", "params": {"videoType": "doubao-seedance-2-5", "videoTime": 5, "imageList": ["https://example.com/product.png"], "templateKey": "product-showcase", "productInfo": "Portable bottle", "resolution": "720p", "aspectRatio": "16:9"}}'
```

以上参数仅为结构示例；必须替换为真实素材、模型和本次任务ID，不能调用示例占位地址执行收费测试。

## 错误处理

HTTP200不保证业务成功。检查error、errcode及code；无成功字段时不要继续依赖链。处理400参数错误、401/403认证或归属失败、402余额不足、404任务不存在及下游错误。模板支持网关ToolErrorResponse XML标准化。不要只依赖脚本退出码，失败响应可能仍被保存为JSON。

未配置Key、401鉴权异常或402余额不足时，读取本skill内置 [onboarding.md](onboarding.md)，按原有AIGC流程引导。403成员归属或权限失败不能通过充值解决。手机号登录、短信及套餐支付按用户选择执行，不自动操作；不将登录Token、验证码或Key写入任务产物。

## Feedback

反馈接口：https://skill-api.linkfox.com/api/v1/public/feedback 。记录路径、requestId/taskId及脱敏错误摘要；参数类型不符、异常响应结构、持续查询失败可反馈。绝不包含Key、Authorization、Base64或私密素材内容。
