# 访谈流程总览（阶段切换条件）

## 阶段图

```
阶段 0：开场与边界确认
  ↓ 专家确认命名 + 授权访谈
阶段 1：访谈（5 维自由深挖）
  ↓ D1-D5 全部达到判定标准（或被 refused）
阶段 2：结构化 + 假设批量确认
  ↓ 专家批量确认 assumed_fields，通过最终校对
阶段 3：生成 skill 文件
  ↓ SKILL.md / references / scripts 全部落盘
阶段 4：交接（提醒评估器）
  ↓
  结束
```

## 状态机（用 interview-record.md 中的 `<!-- interview-progress -->` 标记判定当前处于哪一阶段）

| 当前状态 | 判定依据 | 下一步 |
|---------|---------|-------|
| 无 `references/interview-record.md` | 目录中不存在该文件 | 阶段 0 |
| `round=0` | 刚建完目录骨架，未访谈 | 阶段 1 第一轮 |
| `round=N dim_done=[...]`，且 dim_done 不含 D1-D5 全部 | 访谈中 | 阶段 1，继续下一维 |
| `dim_done=[D1,D2,D3,D4,D5]`，未出现 `structure_confirmed` | 访谈完毕 | 阶段 2 |
| `structure_confirmed=true`，skill 文件未生成 | 校对完成但未落盘 | 阶段 3 |
| skill 文件已存在且 `<!-- interview-progress: ... status=complete -->` | 生成完成 | 阶段 4 |
| 目录下存在 `.eval/report-*.md` 且用户说要迭代 | 评估后回环 | 迭代模式（先读最新报告） |

## 阶段之间的切换条件（严格）

**阶段 0 → 阶段 1**：必须同时满足
- 专家已确认 skill 名
- 同名校验已完成（若撞名，专家已选择覆盖/新增/放弃之一）
- 专家明确同意进入访谈（口头"可以"/"好"/"开始吧"等）

**阶段 1 → 阶段 2**：必须同时满足
- D1-D5 每维都在 interview-record.md 中有非空内容，或被标 `refused`
- 每维满足 `dimension-checklist.yaml` 中定义的最低产出
- D3 每个步骤的 `execution_type` 已明确（script / llm / delegate）；delegate 步骤已通过 `06-delegate-discovery.md` 的搜索与专家确认链路
- 写入 `<!-- interview-progress: round=N dim_done=[D1,D2,D3,D4,D5] -->`

**阶段 2 → 阶段 3**：必须同时满足
- 完成隐私审查（或专家确认没有敏感信息）
- `assumed_fields` 列表已批量确认（每条有 ✓ 或修改记录）
- 5 维概览校对通过（专家回复"可以"/"没问题"/"对"等）

**阶段 3 → 阶段 4**：必须同时满足
- `SKILL.md` / `references/interview-record.md` / `references/workflow.md` / `references/rules-and-boundaries.md` 全部存在
- D3 中每个 `execution_type: script` 步骤都有对应的 `scripts/*.py` 骨架
- D3 中每个 `execution_type: delegate` 步骤的 `delegates_to` 值出现在 SKILL.md frontmatter 的 `depends_on`
- SKILL.md frontmatter 含 `name` / `description` / `authored_by: linkfox-skill-creator` / `interview_record: references/interview-record.md` / `depends_on`
- `depends_on` 中每个 slug 在 `delegate_search_log` 中都有专家确认证据

## 中断与恢复

专家任何时候说"我现在没时间""下次再说""暂停一下"等：
1. 确保 interview-record.md 的 `<!-- interview-progress -->` 标记是最新的
2. 礼貌告知：下次可以直接说"继续上次没完成的 XX skill"
3. 不删任何中间产物

下次触发 Creator 且发现草稿存在时：
1. 读 `<!-- interview-progress -->` 标记
2. 问："我看到您上次做到了 [已完成维度]，要继续还是重新开始？"
3. 继续则从 dim_done 中缺的第一个维度开始

## 迭代模式（评估后回头改）

专家说"根据评估报告改一下""再进化一版"等：
1. 读 `skills/<name>/.eval/report-*.md` 中最新一份的 `publish_advice` 和各维度分数
2. 对分数低 / 标 `revise` 的部分，回到对应的 stage 做局部修改：
   - E1 忠实度问题 → 阶段 2 重新对照 interview-record 确认
   - E2 可读性问题 → 阶段 3 重写生成
   - E3 契约问题 → 阶段 3 修模板或补 scripts
   - E4 行为问题 → 阶段 2/3 补规则 / 补边界
3. 修改完成后再次触发评估，直到 publish_advice ≠ block

## 不允许的跨阶段跳转

- 不能跳过阶段 0 直接开始问 D1（会导致命名/授权缺失）
- 不能跳过阶段 2 直接生成（会丢失隐私审查与假设确认）
- 不能在阶段 1 就生成 skill 文件（只写 interview-record.md 草稿）
