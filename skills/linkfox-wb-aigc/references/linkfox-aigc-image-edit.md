# linkfox-aigc-image-edit

## 功能与边界

用一张源图和编辑提示词完成背景、风格、元素、文字、水印、服装或商品视觉修改。`params.imageUrl`、`params.prompt`、`params.provider` 必填；源图支持 jpg、jpeg、png、webp，通常尺寸 300 至 4096 像素，提示词最多 3000 字符。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/imageEdit` | `aigc/imageEdit` | `{"params":{"imageUrl","prompt","provider",...}}` |
| 查询 | `/aigc/taskQuery` | `aigc/taskQuery` | `{taskId}` |
| 素材上传 | `/aigc/uploadByBase64` | `aigc/uploadByBase64` | `{fileName, base64}` |

可选参数包括 `outputNum`（1 至 4）、`template`、`needOptimize`、`aspectRatio`、`resolution`、`supplyType` 和 `quality`。模板可用于白底图、商品主图精修、场景、海报、换模特、风格调整、移除元素和文字或水印处理；模板中的配置优先于入参可选值。

素材前置上传后使用 `viewUrl`。创建返回 taskId，查询返回 `status`、`resultList[].id/url/type`、`errorMsg` 和可用费用；当前响应未定义的单项字段不得推断。

## 特殊规则

- provider 的比例和分辨率需按模型表核对；GPT 系列 quality 支持 low、medium、high，部分模型另支持 xhigh、max。
- 不把通用生图、多图融合或商品套图请求改写为此接口。
- 源编辑、上传、下载和 onboarding 脚本不进入成品。
