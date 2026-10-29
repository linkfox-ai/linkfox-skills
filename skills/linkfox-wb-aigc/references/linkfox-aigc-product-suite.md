# linkfox-aigc-product-suite

## 功能与边界

从商品图片生成卖点图、场景图、特写图、白底图和普通或高级 A+ 素材。适合商品 Listing 和广告素材批量制作，不是单图精修或服装专用套图。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/productMarketMaterial` | `aigc/productMarketMaterial` | `{"params":{...}}` |
| 查询 | `/aigc/taskQuery` | `aigc/taskQuery` | `{taskId}` |
| 素材上传 | `/aigc/uploadByBase64` | `aigc/uploadByBase64` | `{fileName, base64}` |

生成 `params` 必填 `imageList`。常用字段有 `sellerPoint`、`isExtractPrePoint`、`provider`、`aspectRatio`、`resolution`、`brandKey`、`sellerTypeNum`、`sceneTypeNum`、`closeUpTypeNum`、`closeUpWhiteTypeNum`、`whiteBgTypeNum`、`aPlusNum`、`aPlusProNum`、`aPlusHasPhone`、`aPlusAspectRatio`、`noText`、`aPlusStyles`、`pointStyles`、`sensitiveLibraryId`、`replaceLibraryId` 和 `quality`。各数量通常每类最多 12，卖点未自动提取时 `sellerPoint` 条件必填。

先用上传 endpoint 将本地图片转为 `base64`，保留文件扩展名，成功响应中的 `viewUrl` 才填入 `imageList`。上传失败不创建任务。创建成功返回 taskId；查询返回 `status`、`resultList`、`errorMsg` 和可用费用字段。

## 特殊规则

- A+ 样式列表数量要覆盖对应的 A+ 数量；`aPlusHasPhone` 基于高级 A+ 结果生成手机版。
- `provider`、`quality`、比例和分辨率按当前模型配置，不能从旧下游文档推断不支持的值。
- 创建时费用为零不代表免费；最终费用以查询真实返回为准。源套图、上传、下载和 onboarding 脚本不进入成品。
