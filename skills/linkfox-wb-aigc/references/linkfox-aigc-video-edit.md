# linkfox-aigc-video-edit

## 功能与边界

根据编辑指令修改已有视频，可提供参考图片。`params.sourceVideoUrl`、`prompt`、`videoType` 必填；`prompt` 最多 2500 字符，`videoTime` 和 `refImageList` 可选。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/videoEditing` | `aigc/videoEditing` | `{"params":{"sourceVideoUrl","prompt","videoType",...}}` |
| 查询 | `/aigc/taskQuery` | `aigc/taskQuery` | `{taskId}` |
| 素材上传 | `/aigc/uploadByBase64` | `aigc/uploadByBase64` | `{fileName, base64}` |

模型和时长规则以当前接口模型表为准，包括可灵 V3-Omni、Gemini Omni Flash、豆包 Seedance、HappyHorse、万相和 Seedance 2.5 等；固定时长模型未传 `videoTime` 时使用默认值，跟随原视频模型使用约定的特殊值。创建返回 taskId，查询返回任务状态、结果列表和费用字段。

`sourceVideoUrl` 和每个 `refImageList` 素材先用 `aigc/uploadByBase64` 取得 `viewUrl`。不要使用源文档中的下游版本化路径替换 WorkBuddy endpoint。

## 特殊规则

- 只把画面改变、背景替换或风格修改放进 prompt；翻译和口型同步改用视频翻译，参考视频复刻改用视频复刻。
- 查询结果未提供的单项状态、尺寸、格式或扩展字段不得推断。404 表示 taskId 不存在，403 是权限或归属问题。
- 源视频编辑、上传、下载和 onboarding 脚本不进入成品。
