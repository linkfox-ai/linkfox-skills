# 图片模型目录 接口说明

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

## 接口：查询图片模型目录（modelConfigList）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_AI_API_URL}/image/model/config/list?bizType=201`

本接口为公共配置的例外：使用 GET、5 秒超时，不需要生成 API Key，不发送 Authorization、SESSION_ID、MESSAGE_ID、MODE_ID 或 APP_NAME；仅发送 Referer `https://wiki.linkfox.com/` 和公共 User-Agent。生成网关与配置域名独立。

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| bizType | integer（Query） | 是 | 201 | 图片入口固定 201。 |
| LINKFOX_AI_API_URL | string（环境变量） | 否 | https://ai-api.linkfox.com | 每次读取，去首尾空白和末尾 `/`；支持自定义域名或带路径前缀，未设置、空串或纯空白使用默认值。 |

#### 脚本选项与环境

| 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --list-models | CLI flag | 查询时是 | `python scripts/aigc_imagegen.py --list-models --inline`；只查询配置，不创建任务、不轮询、不下载。 |
| --inline | CLI flag | 否 | 强制完整输出目录，仍保存完整配置。 |
| --allowed-models | JSON array[string] | 否 | 仅在列表查询时使用，按明确的业务限制取交集；空数组表示无可选模型，不能在生成调用中使用。格式错误或用于生成时报错，不当作查询失败。 |
| --no-cache | CLI flag / 内部固定选项 | 否 | 所有公共调用都禁用缓存，目录每次读取当前服务配置。 |

| 环境 | LINKFOX_AI_API_URL | LINKFOX_TOOL_GATEWAY |
|---|---|---|
| 生产 | https://ai-api.linkfox.com | https://tool-gateway.linkfox.com |
| 测试 | https://test-ai-api.linkfox.com | https://test-sz-tool-gateway.linkfox.com |

仅配置网关不会切换目录；测试环境同时设置两个变量。不根据网关域名、Key 或测试前缀推断配置地址，不复用登录、团队或文本模型变量。配置无效或失败沿用静态兜底，不改向生产重试。

### 响应结构

#### 原始公共配置响应

| 字段 | 类型 | 说明 |
|---|---|---|
| code | integer / string | 200 / "200" 表示配置查询成功。 |
| data | array[object] | 模型原始列表，允许为空。 |
| data[].code | string | 必须非空的配置模型标识，不对用户展示。 |
| data[].name | string | 必须非空的模型说明名称，用于用户展示。 |
| data[].apiCode | string | 图片请求依据 apiCode 及兼容别名；未知 code 又无可安全使用 apiCode 时跳过该项。 |
| data[].supportedRatios | array[string] / null | 支持的比例。 |
| data[].supportedResolutions | array[string] / null | 支持的分辨率。 |
| data[].supportedDurations | array[string] / null | 通用配置能力中的时长，存在时原样保留，不变成图片生成参数。 |
| data[].supportedQualities | array[string] / null | 质量档位。 |
| data[].refImageCount | integer | 非负的模型原始参考图上限。 |
| data[].isDefault | boolean | 后台默认标记，不覆盖本技能默认模型 LF智能模型 G-2.5 Sunburst。 |
| data[].isMaintenance | boolean | 维护标记；为 true 时从可选目录移除。 |
| data[].supportVoice / supportLastFrame | boolean | 通用配置能力开关，存在时保留；格式错误触发查询失败兜底。 |
| data[].supportCamera / supportEcoMode / supportPromptExpand | 原值 | 通用配置能力开关，存在时原样保留。 |
| data[].defaultResolution | 原值 | 配置默认分辨率，存在时保留。 |
| data[].extraConfig | object / null | 扩展能力；不与不同渠道的配置合并。 |
| data[].extraConfig.supportModes | array[string] | 模式数组，存在时必须为字符串列表。 |

能力列表存在且非 null 时必须为字符串数组；code/name 必须为非空字符串；refImageCount 存在时须为非负整数；isMaintenance、supportVoice、supportLastFrame 存在时须为布尔值；extraConfig 存在且非 null 时须为对象；其中 supportModes 存在且非 null 时须为字符串数组。完整上游额外字段保留在 rawResponse，不补造未知字段。

#### 脚本目录与输出

| 字段 | 类型 | 说明 |
|---|---|---|
| source | string | remote（查询成功）/ fallback（查询失败）。 |
| bizType | integer | 图片固定 201。 |
| entry | string | 图片固定 image。 |
| models | array[object] | 规范化、渠道去重并排除维护项后的可用模型。 |
| models[].name / code / apiCode | string | 说明名称、配置标识及存在时的下游标识。只展示 name。 |
| models[].requestValue | string | 规范化请求参考值，用于构造新选择，不强制迁移已有生成值。 |
| models[].aliases | array[string] | 去重后的 code、来源请求值、规范值和 name。 |
| models[].isDefault / isMaintenance | boolean | 缺失时默认 false；维护项已过滤。 |
| models[].refImageCount | integer | 图片入口有效上限，取原始上限与 10 的较小值。 |
| models[].modelRefImageCount | integer | 保留模型原始参考图上限；不能用它或 rawResponse 越过入口上限。 |
| models[].supportedRatios / supportedResolutions / supportedDurations / supportedQualities | array[string] / null | 从对应上游字段复制的能力列表。 |
| models[].supportVoice / supportLastFrame / supportCamera / supportEcoMode / supportPromptExpand / defaultResolution / extraConfig | 原值 | 存在时原样复制的能力，不改写生成参数。 |
| rawResponse | object | 查询成功时保存完整原始响应；stdout 不打印此项。 |
| fallbackReason | string | 查询失败时的异常类型，不编造服务端不可用原因。 |
| dataFile | string / null | stdout 中的完整目录文件路径，保存失败仅记录 stderr，不阻断生成。 |
| modelCount | integer | 非 inline 且超过 8000 字节时提供模型总数。 |
| notice | string | 摘要时提示读取完整能力或使用 --inline。 |

普通输出超过 8000 字节时，models 只展示 name/requestValue，完整能力仍在 dataFile；不输出媒体交付标记 `Saved full response`。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- HTTP 基础规则仍按公共规则；本接口还要求 code 为 200 / "200" 且 data 为列表。连接、HTTP、协议读取、业务状态或解析结构错误均返回 source=fallback。
- 成功的空列表、模型缺失或全维护是有效远端结果，不能恢复静态模型；不自动换模型。
- 仅失败才读取同目录 `scripts/aigc_model_fallbacks.json` 的静态目录。该文件不是永久白名单，动态目录中的模型可选。
- 兼容别名和规范值等价，比较前规范化，不能因字符串形式不同误拒绝；重复渠道保留单一记录，不合并能力。

### curl 示例

```bash
curl -sS -X GET "${LINKFOX_AI_API_URL:-https://ai-api.linkfox.com}/image/model/config/list?bizType=201" \
  -H "Referer: https://wiki.linkfox.com/" \
  -H "User-Agent: LinkFox-Skill/2.0"
```

### 静态兜底能力

以下静态说明表仅在查询失败时适用；完整冻结能力保留在 `scripts/aigc_model_fallbacks.json`。图片请求兼容映射与模型参数对照见 [api.md](api.md)，生成操作见 SKILL.md 的“生图流程”，选择与展示规则见“约束与建议”。

| 说明名称 | 支持分辨率 | 参考图上限 | 特点 |
|------|------|------|------|
| LF全能模型 | 1K | 6张 | 基础生成 |
| LF全能模型 2 | 1K/2K/4K | 10张 | 支持更高分辨率 |
| LF全能模型 Pro | 1K/2K/4K | 10张 | 用户指定时使用 |
| LF智能模型 G-2 | 1K/2K/4K | 10张 | 支持 low/medium/high 质量档位 |
| Linkfox-Image-1 | 2K | 4张 | 适合编辑类场景 |
| Wan 2.7 | 1K/2K | 6张 | 创意增强 |
| Seedream 5.0 | 2K | 6张 | 仅支持2K |
| LF智能模型 G-2.5 Sunburst | 1K/2K/4K（首轮未指定时用1K） | 10张 | 支持 low/medium/high/xhigh/max 质量档位 |
| LF智能模型 G-2.5 Flare | 1K/2K/4K（默认2K） | 10张 | 支持 low/medium/high/xhigh/max 质量档位 |
| Seedream 5.0 Pro | 1K/2K | 6张 | 不使用 quality 档位 |

未指定时使用 LF智能模型 G-2.5 Sunburst（`GPT_2_5_IMAGE` / `LF_GT_2`），先用 `1K`、`low` 出图给用户确认。确认画面后，再询问是否用同一模型重出 `2K`、`medium`，得到用户同意后才创建新任务。用户已明确指定的模型、分辨率和质量原样透传，只有明确要求才传 `4K`。

本包自包含 aigc_model_config.py 与 aigc_model_fallbacks.json，不跨技能导入。共用模块和静态文件包含视频目录兼容数据；本技能 CLI 只使用 image 入口，不执行视频生成。视频目录兼容查询说明如下；视频生成需求转交对应技能。用户可见选择与模型名称展示规则统一见 SKILL.md 的“约束与建议”。

## 接口：查询视频模型目录（共用模块兼容分支）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_AI_API_URL}/image/video/model/config/list?bizType=88`

本接口由共用模块发起公开 GET：5 秒超时，只发送 Referer `https://wiki.linkfox.com/` 与 User-Agent，不发送生成 API Key 或任何会话身份头。不由图片 CLI 调用，也不创建视频任务。

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| bizType | integer（Query） | 是 | 88 | video / video_multi 模块入口使用同一个目录。 |
| LINKFOX_AI_API_URL | string（环境变量） | 否 | https://ai-api.linkfox.com | 每次读取，去首尾空白及末尾 `/`，空白时回退默认；与生成网关独立，不根据其他域名或密钥推断。 |
| kind | string（本地函数参数） | 是 | — | `load_catalog("video", allowed_models=None)` 或 `load_catalog("video_multi", allowed_models=None)`；仅控制目录过滤，不发送到接口。 |
| allowed_models | array[string]（本地函数参数） | 否 | None | 必须为非空字符串元素的数组或 tuple，空集合表示无可选模型；按明确的业务限制取交集，不影响生成提交。 |

测试配置域名为 `https://test-ai-api.linkfox.com`，生产默认 `https://ai-api.linkfox.com`；请求失败不改向生产重试。此接口没有独立 CLI，兼容查询通过同目录 Python 模块提供。

### 响应结构

#### 原始配置

| 字段 | 类型 | 说明 |
|---|---|---|
| code | integer / string | 200 / "200" 表示配置查询成功。 |
| data | array[object] | 原始模型列表，允许为空。 |
| data[].code / name | string | 必须为非空字符串；code 用于构造视频请求参考值，name 用于用户展示。 |
| data[].apiCode | string | 存在时保留的下游标识；不是 videoType，不用它代替 code。 |
| data[].supportedRatios | array[string] / null | 支持比例，存在且非 null 时必须为字符串数组。 |
| data[].supportedResolutions | array[string] / null | 支持分辨率，存在且非 null 时必须为字符串数组。 |
| data[].supportedDurations | array[string] / null | 支持时长，存在且非 null 时必须为字符串数组。 |
| data[].supportedQualities | array[string] / null | 质量档位，存在且非 null 时必须为字符串数组。 |
| data[].refImageCount | integer | 非负参考图数量，不按图片入口的 10 张上限截断。 |
| data[].isDefault | boolean | 后台默认标记。 |
| data[].isMaintenance | boolean | 维护标记，为 true 则过滤。 |
| data[].supportVoice / supportLastFrame | boolean | 存在时必须为布尔值。 |
| data[].supportCamera / supportEcoMode / supportPromptExpand / defaultResolution | 原值 | 存在时保留的上游能力值。 |
| data[].extraConfig | object / null | 扩展能力，存在且非 null 时必须为对象。 |
| data[].extraConfig.supportModes | array[string] | 存在时必须为字符串列表，按模式过滤。 |

#### 本地模块返回与输出

| 字段 | 类型 | 说明 |
|---|---|---|
| source | string | remote / fallback。 |
| bizType | integer | 固定 88。 |
| entry | string | video / video_multi，与 kind 相同。 |
| models | array[object] | 规范化、去重、维护过滤、业务交集与模式过滤后的列表。 |
| models[].name / code / apiCode | string | 说明名称、配置代码及存在时的下游标识；仅向用户展示 name。 |
| models[].requestValue | string | 根据 code 规范化的请求参考值；兼容别名 MODEL → KLING、PRODUCT → HAILUO、HAILUO3 → MINIMAX_V2。 |
| models[].aliases | array[string] | code、来源值、规范值与 name 的去重列表。 |
| models[].isDefault / isMaintenance | boolean | 缺失时默认 false。 |
| models[].supportedRatios / supportedResolutions / supportedDurations / supportedQualities | array[string] / null | 存在时复制上游能力列表。 |
| models[].refImageCount | integer | 原始参考图上限；video_multi 要求至少 1。 |
| models[].supportVoice / supportLastFrame / supportCamera / supportEcoMode / supportPromptExpand / defaultResolution / extraConfig | 原值 | 存在时复制的能力，不改写生成请求。 |
| rawResponse | object | 远端成功时完整原始响应；普通目录打印函数排除此项。 |
| fallbackReason | string | 失败时异常类型。 |
| dataFile | string / null | 调用 save_catalog / print_catalog 时的完整目录路径，保存失败为 null。 |
| modelCount / notice | integer / string | 非 inline 输出超过 8000 字节时提供总数和读取完整能力提示，models 仅保留 name/requestValue。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- HTTP 基础判断按公共规则，另要求 code 为 200 / "200"、data 为列表；连接、HTTP、协议读取或解析结构错误才读取同目录冻结文件的 video / video_multi 静态目录。
- 远端成功为空、缺失或全维护时不补回静态模型；普通场景不以静态目录封顶，不自动切换模型。
- video：存在 supportModes 时，必须包含 refImage 或 firstLastFrame 至少一个；video_multi：存在 supportModes 时必须含 refImage，且有效 refImageCount 至少 1。
- 兼容请求值和规范别名先规范化再比较，不能因形式差异误拒绝；同一请求值仅保留一个渠道，优先规范渠道，不合并不同渠道能力。
- 目录存档失败仅记录 stderr，不作为生成前置条件，查询结果不改写视频默认、参数、模式或生成请求。此分支仅提供兼容查询，用户的视频生成需求仍转交对应技能。

### curl 示例

```bash
curl -sS -X GET "${LINKFOX_AI_API_URL:-https://ai-api.linkfox.com}/image/video/model/config/list?bizType=88" \
  -H "Referer: https://wiki.linkfox.com/" \
  -H "User-Agent: LinkFox-Skill/2.0"
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-imagegen",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
