# 高级 A+ 与品牌故事模块

按 [A+ Content Management v2020-11-01 官方模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/aplus-content-api-model/aplusContent_2020-11-01.json) 组装 `contentDocument`。下表用于选择模块并核对大小写。组装实际文档前，按所选模块在 [高级 A+ 模块参考](https://developer-docs.amazon/sp-api/docs/a-plus-premium-modules) 或 [品牌故事模块参考](https://developer-docs.amazon/sp-api/docs/a-plus-brand-story-modules) 中检查嵌套字段、图片尺寸、字符数和数组数量。

## 文档结构与回读

- 文档包含 `name`、`locale`、`contentType` 和 `contentModuleList`。卖家商品级 A+ 用 `EBC`，供应商用 `EMC`。高级 A+ 通过 `PREMIUM_*` 模块表示。商品级文档内统一使用 `STANDARD_*` 或 `PREMIUM_*`，两者不能混用。
- 品牌故事用 `contentType: "BrandStory"`，文档只含 `BRAND_STORY_*` 模块，必须包含恰好一个 `BRAND_STORY_IMAGE_WITH_LOGO` 背景卡。商品级 A+ 与品牌故事分别建文档，可关联相同的 ASIN。
- 每个模块对象包含 `contentModuleType` 及其对应的模块数据字段。文本组件形如 `{"value":"标题","decoratorSet":[]}`，段落组件形如 `{"textList":[{"value":"正文"}]}`。
- 搜索结果用 `contentMetadataRecords[].contentMetadata.badgeSet` 中的 `PREMIUM` 标记筛选。回读时请求 `CONTENTS,METADATA`，用 `contentRecord.contentDocument.contentType` 区分品牌故事，用 `contentRecord.contentDocument.contentModuleList` 读取模块。单凭空 `badgeSet` 不判断文档类型。

## 高级 A+ 模块映射

| `contentModuleType` | 模块数据字段 | 官方模型必填字段（模块内第一层） |
|---|---|---|
| `PREMIUM_IMAGE_TEXT` | `premiumImageText` | `positionType`, `headline`, `image` |
| `PREMIUM_TEXT` | `premiumText` | `description` |
| `PREMIUM_FULL_BACKGROUND_TEXT` | `premiumFullBackgroundText` | `positionType`, `colorType`, `desktopImage`, `mobileImage` |
| `PREMIUM_FULL_BACKGROUND_IMAGE` | `premiumFullBackgroundImage` | `desktopImage`, `mobileImage` |
| `PREMIUM_FOUR_COLUMN_IMAGES` | `premiumFourColumnImages` | `columns` |
| `PREMIUM_DUAL_IMAGE_TEXT` | `premiumDualImageText` | `columns` |
| `PREMIUM_IMAGE_CAROUSEL` | `premiumImageCarousel` | `carouselCards` |
| `PREMIUM_NAVIGATION_CAROUSEL` | `premiumNavigationCarousel` | `carouselCards` |
| `PREMIUM_REGIMEN_CAROUSEL` | `premiumRegimenCarousel` | `carouselCards` |
| `PREMIUM_THREE_COLUMN_COMPARISON` | `premiumThreeColumnComparison` | `headline`, `comparisonProducts`, `comparisonRows` |
| `PREMIUM_COMPARISON_CAROUSEL` | `premiumComparisonCarousel` | `headline`, `comparisonProducts`, `comparisonMetrics` |
| `PREMIUM_COMPARISON_SCROLLER` | `premiumComparisonScroller` | `headline`, `comparisonProducts`, `comparisonRows` |
| `PREMIUM_HOTSPOT_IMAGE` | `premiumHotspotImage` | `desktopImage`, `hotSpots` |
| `PREMIUM_HOTSPOT_IMAGE_TEXT` | `premiumHotspotImageText` | `headline`, `desktopImage`, `hotSpots` |
| `PREMIUM_FAQ` | `premiumFaq` | `faqs` |
| `PREMIUM_TECH_SPECS` | `premiumTechSpecs` | `headline`, `techSpecs` |
| `PREMIUM_VIDEO_TEXT` | `premiumVideoText` | `positionType`, `headline`, `video` |
| `PREMIUM_HERO_VIDEO` | `premiumHeroVideo` | `heroVideo` |
| `PREMIUM_VIDEO_IMAGE_CAROUSEL` | `premiumVideoImageCarousel` | `carouselCards` |

`PREMIUM_TEXT` 的 `description.textList` 为 1–11 段，总长最多 5,000 字符。下例是传给创建、更新或关联校验脚本的 `contentDocument` 参数值，实际调用时另传脚本所需的店铺和站点参数。

```json
{
  "name": "Care instructions",
  "contentType": "EBC",
  "locale": "en-US",
  "contentModuleList": [
    {
      "contentModuleType": "PREMIUM_TEXT",
      "premiumText": {
        "headline": {"value": "Cleaning and storage"},
        "description": {
          "textList": [{"value": "Wash with mild soap and let the parts dry before storing."}]
        }
      }
    }
  ]
}
```

### 滚动比较表字段限制

`PREMIUM_COMPARISON_SCROLLER` 按 [官方高级 A+ 模块参考](https://developer-docs.amazon/sp-api/docs/a-plus-premium-modules) 的模块专用规则构参。共享模型中的 `ComparisonProduct` 含可选 `mobileImage`，但此模块不支持移动端图片，不能照搬比较轮播的全部字段。

- `comparisonProducts` 按官方模块说明准备 4–7 项，每项包装为 `{"comparisonProduct": {...}}`；`comparisonRows` 为 5–12 项，每项包装为 `{"comparisonRow": {...}}`。每行的 `comparisonFields` 每项包装为 `{"comparisonField": {...}}`，数量与商品列相同，`position` 对应商品列位置。
- 商品图片使用 `comparisonProducts[].comparisonProduct.desktopImage`，裁切至少为 200 × 225 px；请求省略同层 `mobileImage`。2026-11-04 生产草稿补测中，额外传入的移动图片对象回读为 `null`，省略该字段后创建、更新及回读通过；此处的 `null` 符合模块限制。
- 该限制只适用于滚动比较表。其他模块是否需要或支持 `mobileImage`，仍按各自的官方字段表处理；不能因共享模型允许该字段，就判断所有模块都支持。

### 热点坐标与回读精度

`PREMIUM_HOTSPOT_IMAGE` 的 `hotSpots[].imageHotSpot` 和 `PREMIUM_HOTSPOT_IMAGE_TEXT` 的 `hotSpots[].imageTextHotSpot` 均以 `TextComponent` 表达 `xCoordinate`、`yCoordinate`，其 `value` 是桌面图上的像素坐标字符串，不传百分比。按 [官方热点定位约束](https://developer-docs.amazon/sp-api/docs/a-plus-troubleshooting) 核对 1464 × 600 px 桌面图：x 在 23–1441、y 在 23–577 范围内，热点之间至少相隔 95 px。

2026-11-04 生产草稿补测中，两种热点模块均出现以下原始回读差异；请求和响应中的值均为字符串：

| 请求 `value` | 回读 `value` | 差异 |
|---|---|---|
| `"200"` | `"199.9824"` | 存在数值偏差。 |
| `"180"` | `"180.0"` | 数值相同，字符串格式不同。 |
| `"500"` | `"499.95599999999996"` | 存在数值偏差。 |

本轮最大数值偏差约为 0.044 px，仅为实测观察值，不是官方精度上限或默认验收容差。数值形态吻合百分比保留两位后再换算为像素的模式，但转换公式属于推断，不能作为接口契约或据此反向修正响应。

创建或更新后回读热点，保留原请求和原始响应，分别核对字符串格式与实际数值偏差，并按任务要求判断定位精度；HTTP 200 不代表坐标无损。1464 × 600 px 背景上的像素字符串 `(366.0, 150.0)`、`(732.0, 300.0)` 在本轮对照样例中回读一致，仅证明这两点通过，不要求将用户坐标改为该网格，也不证明任意坐标无损。

## 品牌故事模块映射

| `contentModuleType` | 模块数据字段 | 官方模型必填字段（模块内第一层） |
|---|---|---|
| `BRAND_STORY_IMAGE_WITH_LOGO` | `brandStoryImageWithLogo` | `desktopImage`, `mobileImage` |
| `BRAND_STORY_FOUR_ASIN` | `brandStoryFourAsin` | `title`, `asinImages` |
| `BRAND_STORY_MEDIA_ASSET` | `brandStoryMediaAsset` | `image` |
| `BRAND_STORY_ABOUT` | `brandStoryAbout` | `logoImage` |
| `BRAND_STORY_QUESTIONS` | `brandStoryQuestions` | `questionAnswerPairs` |

背景卡的桌面图至少为 1464 × 625 px，移动图至少为 463 × 625 px。`brandStoryFourAsin.asinImages` 要求 4 项，`brandStoryQuestions.questionAnswerPairs` 要求 3 项。以官方模块参考中的嵌套结构为准。示例里的上传标识需要替换成对应素材实际上传成功后的 `uploadDestinationId`。

```json
{
  "name": "Our brand story",
  "contentType": "BrandStory",
  "locale": "en-US",
  "contentModuleList": [
    {
      "contentModuleType": "BRAND_STORY_IMAGE_WITH_LOGO",
      "brandStoryImageWithLogo": {
        "desktopImage": {
          "uploadDestinationId": "DESKTOP_UPLOAD_DESTINATION_ID",
          "altText": "Workbench with hand tools",
          "imageCropSpecification": {
            "size": {
              "width": {"value": 1464, "units": "pixels"},
              "height": {"value": 625, "units": "pixels"}
            }
          }
        },
        "mobileImage": {
          "uploadDestinationId": "MOBILE_UPLOAD_DESTINATION_ID",
          "altText": "Detail of the workbench",
          "imageCropSpecification": {
            "size": {
              "width": {"value": 463, "units": "pixels"},
              "height": {"value": 625, "units": "pixels"}
            }
          }
        }
      }
    }
  ]
}
```

## 素材与视频

需要上传新素材时，先确认 `linkfox-amazon-store-uploads` 已安装且其脚本可用，缺失时先安装。已有上传成功的资源标识可直接复用。A+ 使用资源路径 `aplus/2020-11-01/contentDocuments`；推荐通过 Uploads 的创建目的地脚本传 `uploadFile: true`，在同一进程内申请目的地并完成 multipart POST，原始签名地址仅在内存中传递。脚本把目的地 URL 查询参数移入表单，文件字段放在最后。 [Amazon A+ 上传与校验流程](https://developer-docs.amazon/sp-api/docs/create-edit-publish-aplus-content)

以下为 Uploads 创建及上传脚本的输入示例。替换店铺、站点与本地文件路径后，在当前任务工作目录运行 `python <Uploads技能路径>/scripts/create_upload_destination_for_resource.py '<JSON参数>'`。A+ 的 `uploadMethod` 默认 POST。结果分阶段保存，确认上传阶段 `success: true` 后，从创建阶段的 `resolvedUploadDestination.uploadDestinationId` 取资源标识。输出文件可能包含临时签名凭据，不要对外分享；已有目的地也可交独立上传脚本使用。

```json
{
  "sellerId": "SELLER_ID",
  "region": "NA",
  "marketplaceId": "ATVPDKIKX0DER",
  "resource": "aplus/2020-11-01/contentDocuments",
  "uploadFile": true,
  "filePath": "./assets/brand-desktop.png",
  "contentType": "image/png"
}
```

确认上传响应为 2xx 后，才在图片组件中引用该素材的 `uploadDestinationId`，并填写 `altText` 和 `imageCropSpecification.size`。裁剪区域须在源图范围内。

调用方已在内存中持有原始目的地时，仍可使用 Uploads 的独立 `upload_to_destination.py`，A+ 表单目的地显式传 `method: "POST"`。直接 PUT 目的地沿用该脚本的默认方式。

### 视频媒体注册与回读

视频和缩略图上传成功后，运行 `scripts/create_media.py` 注册媒体，运行 `scripts/get_media.py` 回读媒体和配对。两个具名入口负责依赖检查、参数映射和业务结果判断，再委托包内公共调用器请求 `POST /spApi/developerProxy`。调用时传入同一授权店铺的 `sellerId` 和 `region`，外层认证、响应判断和数据落盘沿用 [API 参考](api.md) 及 [脚本约定](script-usage.md)。

| 操作 | `method` | `path` |
|---|---|---|
| 注册媒体或视频缩略图配对 | `POST` | `aplus/2020-11-01/media` |
| 回读媒体、处理状态及配对 | `GET` | `aplus/2020-11-01/media/{mediaId}` |

`create_media.py` 接收 `mediaRequest` 对象，将其序列化为 JSON 字符串放入外层 `body`，并设置 `contentType: "application/json"`。注册素材时，顶层恰好提供 `uploadDestinationId` 或 `mediaId` 中的一项。新上传文件用 Uploads API 返回的原始 `uploadDestinationId`，复用已有媒体用 `mediaId`。

先注册已上传的缩略图。以下是上游 `createMedia` 请求对象，替换其中的占位上传标识。

```json
{
  "mediaType": "IMAGE",
  "uploadDestinationId": "THUMBNAIL_UPLOAD_DESTINATION_ID",
  "title": "Product demonstration thumbnail"
}
```

从响应体取得缩略图的 `mediaId` 后，注册已上传的视频。视频必须有至少一条 `descriptions`，每项包含 `locale` 和无障碍说明 `value`，语言不能重复且须受 Amazon 支持。`relatedMedia` 恰好一项，`associationType` 为 `VIDEO_PAIRING`，`title` 至少三个词且不能全部大写，`media.mediaType` 为 `IMAGE`。配对图片中的 `uploadDestinationId` 与 `mediaId` 同样二选一。下例复用刚取得的缩略图 `mediaId`。 [官方媒体错误与约束说明](https://developer-docs.amazon/sp-api/docs/a-plus-troubleshooting#media-api)

```json
{
  "mediaType": "VIDEO",
  "uploadDestinationId": "VIDEO_UPLOAD_DESTINATION_ID",
  "descriptions": [
    {
      "locale": "en-US",
      "value": "A demonstration of cleaning and storing the product."
    }
  ],
  "relatedMedia": [
    {
      "associationType": "VIDEO_PAIRING",
      "title": "Product care demonstration",
      "media": {
        "mediaType": "IMAGE",
        "mediaId": "THUMBNAIL_MEDIA_ID"
      }
    }
  ]
}
```

在本 Skill 目录运行以下具名入口示例注册缩略图。将店铺和上传标识替换为实际值，`region` 按授权区域填写。注册视频时，将 `mediaRequest` 的值替换为上面的完整视频请求对象。

```bash
python scripts/create_media.py '{"sellerId":"SELLER_ID","region":"NA","mediaRequest":{"mediaType":"IMAGE","uploadDestinationId":"THUMBNAIL_UPLOAD_DESTINATION_ID","title":"Product demonstration thumbnail"}}' --no-cache
```

检查网关外层结果和内部 `httpStatus`。上游 201 表示新建成功，200 表示相同元数据的媒体或配对已存在并返回原有数据，409 表示元数据冲突，需先回读已有数据并按用户意图处理。创建成功后，从上游 JSON 的顶层 `mediaId` 取视频 ID，从 `relatedMedia[].media.mediaId` 取与视频配对的缩略图 ID。 [createMedia](https://developer-docs.amazon/sp-api/reference/createmedia)

回读媒体时，脚本编码 `mediaId` 路径段并使用上表的 `GET` 路径，外层省略 `body`。可选的 `associatedMediaId` 用于只查指定缩略图配对，脚本将其编码到查询串。

```bash
python scripts/get_media.py '{"sellerId":"SELLER_ID","region":"NA","mediaId":"VIDEO_MEDIA_ID","associatedMediaId":"THUMBNAIL_MEDIA_ID"}' --no-cache
```

检查视频和配对的 `status`、`issues`，处理完成且可用后，再把下例的模块对象加入高级 A+ 文档。`imageCropSpecification` 描述缩略图的裁剪范围，尺寸须符合所选视频模块的要求。

```json
{
  "contentModuleType": "PREMIUM_HERO_VIDEO",
  "premiumHeroVideo": {
    "heroVideo": {
      "videoMediaId": "VIDEO_MEDIA_ID",
      "imageMediaId": "THUMBNAIL_MEDIA_ID",
      "imageCropSpecification": {
        "size": {
          "width": {"value": 1464, "units": "pixels"},
          "height": {"value": 600, "units": "pixels"}
        }
      }
    }
  }
}
```

`PENDING_PROCESSING`、`PENDING_REVIEW` 或 `PENDING_AMAZON` 需要等待处理，`UNABLE_TO_PROCESS`、`NOT_APPROVED` 或 `PENDING_SELLING_PARTNER` 需要结合 `issues` 处理，`AVAILABLE` 表示可用于展示。`get_media.py` 每次只回读一次；需等待时按用户范围设定总时限、次数和间隔，到上限后保留媒体 ID、当前状态及续查命令。保留媒体 ID 并按需回读，`mediaUrl` 会失效。 [Amazon A+ 媒体流程](https://developer-docs.amazon/sp-api/docs/create-edit-retrieve-aplus-media)

提交实际文档前，按 [API 参考](api.md) 调用关联校验，检查响应中的验证错误。HTTP 200 仅表示校验已执行。
