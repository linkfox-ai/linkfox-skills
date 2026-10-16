# LinkFox 图转视频

子能力标识 `linkfox-aigc-image-to-video`。创建 endpoint `/aigc/imageToVideo`，精确 `toolName` 为 `aigc/imageToVideo`；查询 endpoint `/aigc/taskQuery`，精确 `toolName` 为 `aigc/taskQuery`。

先读 [video-common.md](video-common.md) 的素材准备、模型命名、查询与交付规则。全部业务调用通过 `LinkFox.proxy_call`，WorkBuddy 自动注入 Authorization，不传凭证，不运行旧网关或自动轮询脚本。下面模型表为随包参数参考，不宣称实时模型配置或价格；不要跨入口套用支持范围。

## 原生请求外层与 params

原生请求外层为 `requestId`、`chatId`、`messageId`、`title`、`params`，所有业务字段放 `arguments.params`，不传顶层 `memberId`。完整外层与响应契约见 [material-common.md](material-common.md)。素材辅助 endpoint `/aigc/uploadByBase64`，精确 `toolName` 为 `aigc/uploadByBase64`；本地与外部URL都先按 [aigc-upload.md](aigc-upload.md) 换成 `viewUrl`。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.videoType | String | 是 | 模型类型；具体支持值见下方各模型参数支持情况|
| params.videoTime | number | 是 | 视频时长（秒）；具体支持值见下方各模型参数支持情况 |
| params.video | List<String> | 可选或条件必填 | 参考视频 URL 列表；支持模型、数量、格式及计费规则见下方参考视频|
| params.promptOptimizer | Boolean | 可选或条件必填 | 是否开启提示词优化；true：开启，false：不开启；默认 false |
| params.isPro | Boolean | 可选或条件必填 | 是否开启高质量 / Pro 模式（已废弃，建议改用 resolution）；兼容规则见下方各模型参数支持情况 |
| params.voice | Boolean | 可选或条件必填 | 是否生成声音；具体支持模型及限制见下方各模型参数支持情况 |
| params.lastFrameImageUrl | String | 可选或条件必填 | 尾帧图地址；具体支持模型及限制见下方各模型参数支持情况|
| params.camera | String | 可选或条件必填 | 运镜参数；具体支持模型及可选值见下方各模型参数支持情况|
| params.templateKey | String | 可选或条件必填 | 视频模板标识，传入后走模板模式，由服务端根据模板配置自动生成最终 prompt，无需手动传 prompt；固定可选值：；product-showcase：产品展示，适合多角度展示商品外观、材质、细节；ugc-seeding：UGC种草，适合用户视角真实分享体验；pain-solution：痛点解决，适合先呈现痛点再演示产品解决方案；furniture-scene：家居场景，适合展示家具/家居用品在真实室内空间中的摆放、搭配和使用效果；注意：与 prompt 互斥，传了 templateKey 则忽略 prompt|
| params.productInfo | String | 可选或条件必填 | 商品信息（模板模式使用），描述商品特征用于生成更精准的视频 prompt；各模板关注维度：；• product-showcase：展示目标、外观重点、展示点、细节路径、场景化使用、主体锚点；• ugc-seeding：口播素材、推荐点、使用动作、人物/商品锚点、适用场景；• pain-solution：痛点、问题对象、前后状态、解决动作、可观察结果、口播素材；• furniture-scene：空间类型、房间布局、家具摆放、材质色彩、搭配元素、使用动作、光线氛围、镜头重点|
| params.language | String | 可选或条件必填 | 目标语言（模板模式使用）；默认 英文|
| params.saleCountry | String | 可选或条件必填 | 销售国家/地区（模板模式使用）；默认 美国|
| params.imageUrl | String | 可选或条件必填 | 原图地址（单图/首帧模式必传）；格式： jpg、jpeg、png、webp；happyhorse-v2 / minimax-h3-lite 不支持，其他模型的具体支持模式见下方各模型参数支持情况|
| params.imageList | List<String> | 可选或条件必填 | 多图参考图列表；kling-v3-omni：1～7 张；kling-v2-6：1～2 张；gemini-omni-flash：1～10 张；doubao-seedance-2-5：1～30 张；wan3：1～10 张；doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / happyhorse-v2 / minimax-h3 / minimax-h3-lite：1～9 张；imageUrl 与 imageList 二选一；happyhorse-v2 / minimax-h3-lite 必须传 imageList|
| params.prompt | String | 可选或条件必填 | 视频提示词（4000 字以内）；注意：不传 templateKey 时必须传 prompt|
| params.resolution | String | 可选或条件必填 | 视频分辨率；具体支持值、默认值及必传规则见下方各模型参数支持情况|
| params.aspectRatio | String | 可选或条件必填 | 视频比例；具体支持值及必传/自适应规则见下方各模型参数支持情况|

### 各模型参数支持情况

以下为随包模型参数参考，执行仍需满足当前接口的实际限制。

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
| 参考图片 | `imageList` | 见上方请求体中的 `imageList` | 数量上限由模型配置决定 |
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


## 模式与条件约束

- `imageUrl` 与 `imageList` 二选一；HappyHorse及MiniMax H3 Lite必须用 `imageList`。不传 `templateKey` 时必须传 `prompt`，最多4000字；模板模式不传 `prompt`，使用 `productInfo/language/saleCountry` 描述商品与市场要求。
- 模板只允许 `product-showcase`、`ugc-seeding`、`pain-solution`、`furniture-scene`，不编造模板标识。运镜 `camera` 只有在已知当前模型支持且有明确合法值时才传；本页没有列出完整枚举，不凭空填写。
- 可灵V3-Omni多图模式必传 `aspectRatio`，仅 `1:1/16:9/9:16`；其首尾帧模式用自适应，不传比例，尾帧仅1080p且无声。可灵2.6声音仅1080p，尾帧也仅1080p且无声，不能同时要求声音与尾帧。
- `video` 最多1段且是数组，不能写成 `refVideoUrl` 或内部 `referenceVideo`；不能同时传尾帧。参考视频模式与首尾帧模式互斥，不自动丢弃用户素材来规避冲突。
- 上传接口单文件限10MB，即使下方业务模型支持100MB或200MB，也必须满足更小的上传限制。参考视频可能按基础扣点2倍计费，新增参考视频需要用户要求覆盖该费用影响。
- 时长、分辨率及参考图上限按本页模型表，不能沿用旧 `videoGenAsync` 的静态值或 `SEED/KLING` 别名；Fast和Mini均不支持1080p。

## MCP 创建示例

示例仅说明结构；执行前替换真实素材与唯一请求ID。专用视频示例的素材必须是上传返回的 `viewUrl`，不能用占位URL做收费测试。

```json
{"toolName":"aigc/imageToVideo","arguments":{"requestId":"<unique-image-to-video-request>","params":{"imageList":["https://example.com/uploaded-product-viewUrl.jpg"],"videoType":"doubao-seedance-2-5","videoTime":10,"templateKey":"product-showcase","productInfo":"用户已确认的商品外观和细节信息","language":"英文","saleCountry":"美国","resolution":"720p","aspectRatio":"9:16"}}}
```

成功创建保存 `taskId`，再按 [video-common.md](video-common.md) 查询 `aigc/taskQuery`。只有 `SUCCESS` 时交付实际视频URL；失败或超时不自动重建，下载失败只补下载。认证、积分与权限错误按 [onboarding.md](onboarding.md)。
