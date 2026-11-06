# 业务流程详述：服饰套图

## 业务目标

用户上传服饰图片（上装/下装/连衣裙/外套/鞋帽等），本技能作为编排层统一规划出图方案（卖点推理 + 画面设计），然后由本地单任务模块按类型构建参数并调用下游生成（agent 套图运行时不 Read types），最终交付一组成套的电商图片。

## 输入参数清单

| 参数 | 性质 | 默认 | 说明 |
|------|------|------|------|
| imageUrls | 运行时入参，必填 | — | 用户上传的服饰图片 URL 列表 |
| provider | 运行时入参 | GPT_2_5_IMAGE | 默认 LF智能模型 G-2.5 Sunburst；用户指定时原样透传当前可用 requestValue |
| resolution | 运行时入参 | 1K | 首轮预览；确认画面后询问是否重出 2K、medium；只有用户明确要求才传 4K |
| quality | 运行时入参 | low | 首轮预览；用户指定时原样透传 |
| point | agent 层传入（可空） | — | 完整卖点描述（≥2句话），有则跳过卖点推理 |
| pointHint | agent 层传入（可空） | — | 方向性关键词（需扩写） |
| imageDesc | agent 层传入（可空） | — | 完整画面描述，有则跳过画面推理 |
| 比例 | 前端传入（可空） | 1:1 | 非A+图的统一比例 |
| A+图比例 | 前端传入（可空） | 按子类型默认 | A+图专用比例 |

## 步骤概览

| 编号 | 动作 | 上游 | 下游 | 调用能力 |
|------|------|------|------|----------|
| S0 | 场景路由 | 用户消息 | S1/S2/S3 | 内部逻辑判断 |
| S1 | 内容推理（卖点/画面/desc/layout） | S0 | S2 | plan 阶段调用 textgen |
| S2 | 确认 plan 已落盘的 image-plan.json | S1 | S3 | Markdown 表格 + AskUserQuestion；修改后以 plan --state 同步 |
| S3 | 一个 dispatch 内部并发 run_one_task + summary | S2 | 用户 | `run_one_task.py` + summary phase |

## 类型路由关系

- WHITE_BG → `references/types/white-bg.md`（①静态直出）
- MODEL_IMAGE → `references/types/model-image.md`（②占位符直出）
- SCENE → `references/types/scene.md`（③textgen 改写）
- SELLING_POINT → `references/types/selling-point.md`（③textgen 改写）
- PREMIUM_APLUS / STANDARD_APLUS / PHONE_APLUS → `references/types/aplus.md`（③textgen 改写）
- SIZE → `references/types/size.md`（阶段1③textgen + 阶段2②占位符直出）

## 已知局限

- 套图编排层不亲自出图，图片质量取决于共享流水线中各类型的参数组装与生图接口
- 多商品场景不支持自动拆分为独立套图，需用户分次上传
- 卖点推理基于 AI 理解，可能不完全准确，用户可在步骤二确认时修改
- 品牌基因提取结果依赖上传图片质量，低分辨率图片可能影响提取准确性
