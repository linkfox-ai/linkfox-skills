# LinkFox 图像生成

子能力标识 `linkfox-aigc-imagegen`。适用于提示词文生图或参考图创作；直接修改已有原图优先使用智能修图，商品营销素材组合优先使用对应套图。

## MCP 契约

- `LinkFox.proxy_call` 创建 endpoint `/aigc/imageGenAsync`，精确 `toolName` 为 `aigc/imageGenAsync`；查询 endpoint `/aigc/taskQuery`，精确 `toolName` 为 `aigc/taskQuery`。
- 请求字段直接位于 `arguments`，不包 `params`、`body` 或 `data`。WorkBuddy 自动注入 Authorization，不传凭证。
- 参考素材需公开可访问；本地文件按 [file-upload.md](file-upload.md) 上传，保持 `imageUrls` 顺序。没有参考图时可省略或传空数组。

## 创建参数与内部模型映射

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| imageUrls | array[string] | 否 | - | 参考图列表；不传或传空列表时为文生图，传入时为参考图生图，具体上限以所选模型配置为准，入口最多10张；下表列出已知模型限制 |
| prompt | string | 是 | - | 提示词，描述期望生成的图片内容 |
| provider | string | 否 | LF全能模型 Pro | 内部模型请求值，按下方“内部执行映射”填写；不得向用户展示该字段值 |
| outputNum | integer | 否 | 1 | 输出张数，取值范围 [1, 10]；未传时默认1 |
| resolution | string | 否 | 按模型 | 分辨率：`1K` / `2K` / `4K`，必须使用所选模型支持的值。两个 G-2.5 模型未指定时默认2K；旧模型保留原调用默认行为 |
| aspectRatio | string | 否 | 由下游决定 | 宽高比以所选模型配置为准；工具端未指定时不透传此字段，建议显式传入合法比例 |
| quality | string | 否 | high | 图片质量：`low` / `medium` / `high` / `xhigh` / `max`；仅支持质量档位的模型生效 |

### 内部执行映射（禁止向用户展示）

面向用户的回复、选项、确认和错误解释必须使用“说明名称”，禁止输出内部请求值。

| 说明名称 | provider 内部请求值 |
|------|------|
| LF全能模型 | `LF_BN_1` |
| LF全能模型 2 | `LF_BN_2` |
| LF全能模型 Pro | `LF_BN_3` |
| LF智能模型 G-2 | `LF_GT_1` |
| Linkfox-Image-1 | `LF_AD_1` |
| Wan 2.7 | `LF_WN_1` |
| Seedream 5.0 | `LF_SD_1` |
| LF智能模型 G-2.5 Sunburst | `LF_GT_2` |
| LF智能模型 G-2.5 Flare | `LF_GT_2_F` |
| Seedream 5.0 Pro | `LF_SD_2` |

工具端兼容历史请求值；本能力新请求使用上表别名，不自行混用套图与修图模型枚举。未传 provider 时按 LF全能模型 Pro 执行。

### 新增图片模型参数支持对照（随包参考）

| 参数 | LF智能模型 G-2.5 Sunburst | LF智能模型 G-2.5 Flare | Seedream 5.0 Pro |
|------|:---:|:---:|:---:|
| resolution | 1K/2K/4K（默认2K） | 1K/2K/4K（默认2K） | 1K/2K |
| imageUrls上限 | 10张 | 10张 | 6张 |
| quality | low/medium/high/xhigh/max | low/medium/high/xhigh/max | 不使用 |
| aspectRatio | 1:1/3:4/4:3/2:3/3:2/9:16/16:9/4:5/5:4/21:9/9:21 | 1:1/3:4/4:3/2:3/3:2/9:16/16:9/4:5/5:4/21:9/9:21 | 1:1/3:4/4:3/9:16/16:9/3:2/2:3/21:9 |

模型表为随包参考，不宣称实时模型配置或费用。已知旧模型限制：LF全能模型仅1K，Seedream 5.0仅2K，LF智能模型 G-2 的 quality 仅 low/medium/high。未列明的比例、分辨率和参考图组合不凭其他接口推断；必要时补充用户选择或报告缺少模型配置，不试探收费调用。

## 创建及查询示例

```json
{"toolName":"aigc/imageGenAsync","arguments":{"imageUrls":[],"prompt":"Studio photograph of a ceramic cup","provider":"LF_BN_3","outputNum":1,"resolution":"1K","aspectRatio":"1:1"}}
```

示例仅展示结构，执行需要用户真实需求。成功创建返回 `taskId`，不是图片URL。

```json
{"toolName":"aigc/taskQuery","arguments":{"taskId":"<returned-taskId>"}}
```

| 查询字段 | 说明 |
|---|---|
| `taskId` | 原任务编号 |
| `status` | `PROCESSING` / `SUCCESS` / `FAILED` |
| `resultList[].id` | 资源ID |
| `resultList[].url` | 图片URL，仅成功后使用 |
| `resultList[].type` | 媒体类型 |
| `errorMsg` | 失败原因 |

每次创建仅调用一次，创建后可查询一次。处理中返回原编号，建议至少等10秒，后续用户明确继续时再次查询，不自动循环、重建、换模型或改素材。成功但媒体为空时报告异常。下载只处理实际成功URL，使用主文档的本地下载辅助。

## 错误处理

业务 `errcode/errorCode` 存在时200表示成功，HTTP或MCP传输成功不保证业务成功。400检查参数；401认证失败、402积分不足、403权限错误按 [onboarding.md](onboarding.md) 分层处理；10009表示任务不存在。保留脱敏错误摘要，不凭空认定扣费或生成成功。
