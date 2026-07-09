# S2 规划确认

- **输入**：S1 产出的 point[] / image_desc[] / desc[] / layout[] + 场景路由确定的类型和数量
- **依赖**：S1（内容推理完成后才能组装方案）
- **操作**：组装 imagePlanList JSON，展示给用户确认
- **输出**：用户确认后的最终 imagePlanList（用户可能要求修改描述/比例或删减条目，以确认后的为准）
- **用途**：确认后作为 S3 的唯一执行依据

---

## 步骤二：输出规划方案给用户确认

展示规划方案供用户确认，仅传入 imagePlanList，参数格式如下。**⚠️ 以下仅为 JSON 格式示例，实际 imagePlanList 中的类型和数量必须严格以场景路由确定的方案为准，严禁照搬示例中的类型列表。**
```json
{
    "imagePlanList":[
        {"type":"SELLING_POINT","point":"具体卖点","desc":"简单描述","image_desc":"画面内容","ratio":"默认比例","layout":"版式标签"},
        {"type":"SCENE","point":"具体卖点","desc":"简单描述","image_desc":"画面内容","ratio":"默认比例","layout":""},
        {"type":"MODEL_IMAGE","point":"","desc":"简单描述","image_desc":"画面内容","ratio":"默认比例","layout":""},
        {"type":"WHITE_BG","point":"","desc":"","image_desc":"","ratio":"默认比例","layout":""}
    ]
}
```

**比例（ratio）约束（必须严格遵守）：**
- **非 A+ 图类型**（种草图、卖点图、模特图、尺码图、白底图）：
    - 若 Context 中 `比例` **不为空**，则使用该值
    - 若 `比例` **为空**，则使用套图类型表中对应的默认比例
- **A+ 图类型**（高级A+图、普通A+图、手机A+图）：
    - 若 Context 中 `A+图比例` **不为空** → 使用 `A+图比例` 的值
    - 若 `A+图比例` **为空**但 `比例` **不为空** → 使用 `比例`（兼容旧流程）
    - 若两者**均为空** → 使用套图类型表中该 A+ 子类型的默认比例（`PREMIUM_APLUS`→`1464:600`、`STANDARD_APLUS`→`970:600`、`PHONE_APLUS`→`600:450`）
    - A+ 图额外支持 `1464:600` / `970:600` / `600:450` 等专属比例（这些比例在非 A+ 图类型中不可用）
- 用户若在确认阶段修改了比例，**必须以用户修改后的值为准**

---

## 展示格式规范

确认前必须先用 Markdown 表格展示 imagePlanList，表头固定 6 列，不可增减：

```
| 序号 | 类型 | 简述 | 卖点 | 画面内容 | 比例 |
|------|------|------|------|----------|------|
```

**格式规则：**
1. 每条条目占且仅占一行；单元格内**禁止出现 `|`、全角 `｜` 或换行**，内容若含竖线/换行须替换为 `/` 或顿号，否则会破坏列对齐，导致表格渲染错位、尾行被甩成纯文本。
2. 卖点、画面内容等关键信息**完整展示、不得截断**（仅需按第 1 条清理竖线与换行）。
3. 空字段统一显示为 `—`（中文破折号），严禁留空。
4. 比例列必填具体值（如 `1:1`、`16:9`）。
5. 类型列用中文名：种草图 / 卖点图 / 模特图 / 尺码图 / 白底图 / 高级A+图 / 普通A+图 / 手机A+图。
6. 表格之后换行调用 `AskUserQuestion` 确认（选项：确认生图 / 修改描述），不要把工具调用写进表格。用户选择修改则按其意见修订 imagePlanList 后重新展示表格并再次确认。

---

## 用户确认后立即落盘（抗上下文压缩，强制）

用户通过 `AskUserQuestion` 确认生图后，**必须在进入 S3 之前**将最终 `imagePlanList` 落盘到 `$DATADIR/image-plan.json`，**禁止**仅在对话上下文保留完整 plan 供 S3 凭记忆重建（S3 上下文已接近压缩阈值，大 Write 极易失败）。

**落盘步骤**（`DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)`）：

1. 初始化：`python <本skill根目录>/scripts/save_image_plan.py --init --out "$DATADIR/image-plan.json"`
2. **逐条追加**（每条任务一次小 Write + 一次 Bash，禁止一次性 Write 整份 plan）：
   - 用 Write 工具写 `$DATADIR/plan-task-01.json`（**仅含单条** imagePlanList 条目，体积通常 < 1KB）
   - `python <本skill根目录>/scripts/save_image_plan.py --append-task-file "$DATADIR/plan-task-01.json" --out "$DATADIR/image-plan.json"`
   - 对第 2…N 条重复（文件名 `plan-task-02.json` …）
3. 落盘完成后，S3 **只读** `$DATADIR/image-plan.json`，不再从上下文重建 JSON。

**Write 失败降级**：若连续 2 次 Write 出现 `required parameter missing` / `InputValidationError`，**停止重试同一次 Write**；改为把该条任务 JSON 拆成更短字段分两次 Write，或向用户说明卡点。
