# 视频任务共同规则

适用于视频生成、多场景视频生成、图转视频、带货口播、商品视频复刻、视频编辑和视频翻译。只读取本次所选能力的参数表，不把其他入口的模型、时长、声音或尾帧能力移植过来。

## 请求结构与素材

| 接口 | 创建请求结构 | 素材准备 |
|---|---|---|
| `aigc/videoGenAsync` | 参数直接放 `arguments` | 首帧 `imageUrl`、可选尾帧 `lastFrameImageUrl` 使用公开URL，本地素材按 [file-upload.md](file-upload.md) 上传 |
| `aigc/multiImageVideoGenAsync` | 参数直接放 `arguments` | 多图 `imageList` 使用公开URL，保留顺序；本地素材按通用文件上传处理 |
| `aigc/imageToVideo` | 原生外层及 `arguments.params` | 按 [aigc-upload.md](aigc-upload.md) 取得每项素材的 `viewUrl` |
| `aigc/salesVideo` | 同上 | 商品等参考图先上传 |
| `aigc/videoReclone` | 同上 | 参考视频 `refVideoUrl` 与商品图 `refImageList` 均先上传 |
| `aigc/videoEditing` | 同上 | 原视频 `sourceVideoUrl` 必须上传，`refImageList` 仅在提供时上传 |
| `aigc/videoTranslation` | 同上 | 只上传 `sourceVideoUrl`，不要求额外图片 |

五个 `params` 接口的原生外层和通用响应另见 [material-common.md](material-common.md)。为每次新创建保存唯一 `requestId`，不传顶层 `memberId`。不调用普通渠道的 HTTP 创建、上传或自动轮询脚本；全部业务请求使用 `LinkFox.proxy_call`，由 WorkBuddy 自动注入 Authorization。

## 模型值不能跨入口复用

`videoGenAsync` / `multiImageVideoGenAsync` 使用 `KLING`、`SEED`、`SEED_FAST` 等内部值，模型显示名称见各自 reference。五个专用视频接口使用自己的公开请求值，例如 `doubao-seedance-2-5`、`kling-v3-omni`。编辑接口的 `WAN3` 与图转视频的 `wan3` 按各自文档填写，不自行改大小写。

| 专用视频请求值 | 用户可读名称 |
|---|---|
| `doubao-seedance-2-0` | 豆包 Seedance 2.0 |
| `doubao-seedance-2-0-fast` | 豆包 Seedance 2.0 Fast |
| `doubao-seedance-2-0-mini` | 豆包 Seedance 2.0 Mini |
| `doubao-seedance-2-5` | 豆包 Seedance 2.5 |
| `minimax-h3` | MiniMax H3 |
| `minimax-h3-lite` | MiniMax H3 Lite |
| `happyhorse-v2` | HappyHorse |
| `wan3` / `WAN3` | 万相 3.0 |
| `kling-v3-omni` | 可灵 V3-Omni |
| `kling-v2-6` | 可灵 2.6 |
| `gemini-omni-flash` | Gemini Omni Flash 1.1 |

这张表只用于显示名称转换，不是各入口的模型白名单。实际允许范围以该能力 reference 为准。随包模型表不代表实时配置或实时价格；参数未知时不试探收费调用。

## 查询、费用与交付

七项视频均用 `/aigc/taskQuery`，精确 `toolName` 为 `aigc/taskQuery`，请求 `arguments.taskId`，不包 `params`，也不使用文本查询接口：

```json
{"toolName":"aigc/taskQuery","arguments":{"taskId":"<returned-video-taskId>"}}
```

创建成功仅表示受理，保存真实 `taskId`。可查询一次；视频通常耗时较长，`PROCESSING` 时交付编号及状态，建议约2分钟后再继续，用户明确继续时用原编号查一次，不自动循环、重新上传或重建。失败展示脱敏 `errorMsg`，成功但结果为空报告异常。网络中断且是否创建未知时，不重新提交。

`status` 使用 `PROCESSING/SUCCESS/FAILED`；仅成功时消费 `resultList[].url`，同时保留实际 `id/type`。不使用下游 `data.id`、数字状态或未透出的扩展字段。实际计费字段若返回则保留原值及单位，缺失记为未知，创建阶段 `costToken=0` 不代表免费。

按用户选定模型、分辨率、视频时长、参考素材和声音需求估算费用影响，缺少实时金额则明确未知。参考视频可能触发额外计费；原视频跟随模式及翻译按服务端读取的真实时长处理，不把文件大小当作时长。未经用户要求不增加变体、试投模型或额外视频。

成功后直接提供视频URL或播放器；需要本地文件时将成功查询业务对象保存为JSON，运行主文档的 `scripts/local/download_results.py`。下载失败只补下载，不重新生成。脚本适用于图片和视频，不承担业务调用或轮询。

生成或改编内容标明 AI 性质，不把复刻、口播或翻译结果当作真实人物背书、真人演示或平台已审核素材。错误分层按 [onboarding.md](onboarding.md)；10007通常表示模型参数组合不合法，10009表示任务不存在，不自动换参数重试。
