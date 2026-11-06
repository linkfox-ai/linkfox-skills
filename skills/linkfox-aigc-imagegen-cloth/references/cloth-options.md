# 服饰编排参数与模型规则

本文记录本地编排及下游参数，不是 `/oss/getStsVoucherByAPI` 的请求体。上传接口定义见 [api.md](api.md)。

## 共享输入参数

以下参数为所有类型通用（类型特有参数见各 type reference）：

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `imageUrls` | string[] | 必填 | 服饰参考图 URL。步骤 1 会校验可访问性 |
| `ratio` | string | 随类型 | 图片比例，原样透传给 imagegen 的 `aspectRatio` |
| `resolution` | string | 1K | 首轮预览用；用户已指定时原样透传 |
| `provider` | string | GPT_2_5_IMAGE | LF智能模型 G-2.5 Sunburst；用户选择其他可用模型时原样透传其 requestValue |
| `quality` | string | low | 首轮预览用；用户已指定时原样透传 |

## 类型路由表

| type | 名称 | 与卖点关联 | 是否有画面描述 | 默认比例 | 支线 | 是否走 textgen | 详情 reference |
|------|------|-----------|-------------|---------|------|---------------|----------------|
| WHITE_BG | 白底图（隐形模特） | 否 | 否 | 1:1 | ①静态直出 | 否 | `references/types/white-bg.md` |
| MODEL_IMAGE | 模特图 | 否 | 是 | 1:1 | ②占位符直出 | 否 | `references/types/model-image.md` |
| SCENE | 种草图 | 是 | 是 | 1:1 | ③textgen 改写 | 是 | `references/types/scene.md` |
| SELLING_POINT | 卖点图 | 是 | 是 | 1:1 | ③textgen 改写 | 是 | `references/types/selling-point.md` |
| PREMIUM_APLUS | 高级A+图 | 是 | 是 | 1464:600 | ③textgen 改写 | 是 | `references/types/aplus.md` |
| STANDARD_APLUS | 普通A+图 | 是 | 是 | 970:600 | ③textgen 改写 | 是 | `references/types/aplus.md` |
| PHONE_APLUS | 手机A+图 | 是 | 是 | 600:450 | ③textgen 改写 | 是 | `references/types/aplus.md` |
| SIZE | 尺码图 | 否 | 是 | 1:1 | 两阶段：①阶段1=③textgen 前置分析 + ②阶段2=占位符直出 | 阶段1是/阶段2否 | `references/types/size.md` |

确定 type 后，**必须 Read** 对应的 type reference 文件获取该类型走哪条支线、步骤 2 差异逻辑和运行时模板来源，**禁止跳过**。

## 动态模型配置（动态完整列表）

本 skill 是普通图片生成场景，**不设置专用模型白名单**。模型从图片 bizType=201 的动态完整列表选择，按参考图数量、比例、分辨率和质量档位等实际任务能力筛选。

在介绍、推荐或确认模型前，按下游文档调用查询模式（实际使用绝对路径）：

```bash
python <linkfox-aigc-imagegen根目录>/scripts/aigc_imagegen.py --list-models --inline
```

- 查询和生成都不注入 `--allowed-models`；编排脚本原样透传所选模型，不额外限制提交参数或改写请求值。
- 返回 `name` 用于展示，`requestValue` 用于构造内部请求。存在于当前列表且满足任务能力的模型，正常接受。
- 只按实际任务能力筛选：参考图数量、支持比例、分辨率和质量档位等。例如不支持参考图的模型不能用于本场景。
- 仅配置查询失败时使用底层返回的静态兜底列表。查询成功时，缺失或维护中的模型不可选，不以请求值示例补入，不自动换模型。
- 缺参时执行下方默认规则。默认参数不符合当前支持范围时提示补充或重选，不跟随后台 `isDefault` 自动替换。

### 动态模型选择与请求值示例

本 skill 不限定模型枚举。当前可选模型以底层动态完整列表及任务能力为准；下表为请求值示例，不是可选模型的完整清单。未传模型时按下方默认规则执行。

| 模型名称 | 内部代码 |
|---------|---------|
| LFBanana Pro | `BANANA_PRO` |
| Img2 | `GPT_2_IMAGE` |
| Img2.5 sunburst | `GPT_2_5_IMAGE` |
| Img 2.5 flare | `GPT_2_5_F_IMAGE` |
| LFBanana2 | `BANANA_2` |
| Linkfox-Image-1 | `AIDRAW_EDIT` |
| Wan 2.7 | `WAN2_7` |

### 默认与确认

未指定时使用 LF智能模型 G-2.5 Sunburst（`GPT_2_5_IMAGE` / `LF_GT_2`），先用 `1K`、`low` 出图给用户确认。确认画面后，再询问是否用同一模型重出 `2K`、`medium`，得到用户同意后才创建新任务。用户已明确指定的模型、分辨率和质量原样透传，只有明确要求才传 `4K`。

默认模型或规格不可用时，按动态目录提示重选。确认预览画面后才询问是否提高规格，用户明确要求的参数优先。
