# linkfox-aigc-clothing-suite

## 功能与边界

从服装参考图生成模特图、卖点图、种草图、尺码图、白底图和普通或高级 A+ 素材。适合服装商品视觉套图，不替代通用商品套图或单图编辑。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/wearCollection` | `aigc/wearCollection` | `{"params":{...}}` |
| 查询 | `/aigc/taskQuery` | `aigc/taskQuery` | `{taskId}` |
| 素材上传 | `/aigc/uploadByBase64` | `aigc/uploadByBase64` | `{fileName, base64}` |

生成 `params` 必填 `imageList`。常用字段有 `sellerPoint`、`isExtractPrePoint`、`provider`、`aspectRatio`、`resolution`、`brandKey`、`modelTypeNum`、`sellerTypeNum`、`insTypeNum`、`sizeTypeNum`、`whiteTypeNum`、`aPlusNum`、`aPlusProNum`、`aPlusHasPhone`、`aPlusAspectRatio`、`modelImageUrl`、`sceneImageUrl`、`isExactScene`、`modelAndSceneInfo`、`noText`、`aPlusStyles`、`pointStyles`、`sensitiveLibraryId`、`replaceLibraryId` 和 `quality`。各数量通常每类最多 12。

`modelImageUrl` 和 `sceneImageUrl` 可启用指定模特或场景；缺失时使用智能模式。外部或本地素材先经 `aigc/uploadByBase64`，随后只传返回的 `viewUrl`。创建返回 taskId，使用共享 `aigc/taskQuery` 查询终态。

## 特殊规则

- `isExactScene` 为 true 时遵循场景，false 时进行相似裂变；不要在用户没有说明时擅自改变语义。
- A+ 样式和数量必须匹配；provider、比例、分辨率和质量按当前模型配置。
- 源套图、上传、下载和 onboarding 脚本不进入成品。
