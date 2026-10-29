# linkfox-aigc-imagegen

## 功能与边界

通用文生图和参考图生图。`imageUrls` 不传或为空表示文生图，传入时表示参考图生图；单次 `outputNum` 为 1 至 10。模型说明名称和参考图上限优先读取当前动态图片模型配置，查询失败才使用源能力的静态兜底。

不用于单图精修、多图融合、商品套图或视频生成。素材若不是可访问的 URL，不能直接提交本地路径；本入口的预期路由没有独立上传 endpoint，先取得可访问 URL 再调用。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/imageGenAsync` | `aigc/imageGenAsync` | `{prompt, imageUrls?, provider?, outputNum?, resolution?, aspectRatio?, quality?}` |
| 查询 | `/aigc/taskQuery` | `aigc/taskQuery` | `{taskId}` |

创建必填 `prompt`。可选字段包括 `imageUrls`、`provider`、`outputNum`、`resolution`、`aspectRatio` 和 `quality`。默认模型说明名称为 LF全能模型 Pro；内部请求值由模型映射构造，但不得向用户展示。生成模型的分辨率、比例、质量档位和参考图数量必须以动态配置为准。

创建成功只返回 `taskId`。查询返回 `taskId`、`status`、`resultList[]` 和失败时的 `errorMsg`；结果项通常有 `id`、`url`、`type`。状态为 `PROCESSING` 时继续查询，`SUCCESS` 才交付结果，`FAILED` 不重建任务。

## 特殊规则

- 初始轮询间隔约 10 秒，逐步降至 5 秒，客户端最长等待 600 秒；超时只返回原 taskId。
- 质量档位只对支持它的模型生效；Seedream 5.0 Pro 不使用 quality。模型代码只留在请求内部。
- `errcode` 或 `errorCode` 为 400/10007 时核对参数；401、402 按主文档认证章节处理；10009 表示 taskId 不存在。
- 源 `aigc_imagegen.py`、模型查询脚本、fallback JSON 和 onboarding 脚本属于旧传输或配置运行时，不随本 WorkBuddy 包分发。
