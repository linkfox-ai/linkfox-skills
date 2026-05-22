# 04 E4 行为符合

回答一个问题：**让一个 agent 加载这份 skill 去跑一个真实任务（含反例），它的行为跟 skill 写的对得上吗？**

这是动态评估，也是 overall_score 权重最高（35%）的维度。

## 输入前提

- E3 pass（scripts/ 齐全可执行）
- E2 score ≥ 60（skill 能被读懂）
- 目标 skill 的 SKILL.md、references/、scripts/ 完整

## 执行顺序

```
1. 主 agent 构造合成任务（见 05-synthetic-task.md）
2. 主 agent 构造反例集（见 06-counter-example.md）
3. spawn 子 agent C：跑合成任务
4. spawn 子 agent D：跑反例集（每个反例独立子会话，避免上下文污染）
5. 主 agent 核查子 agent 轨迹，计算 5 个子分
6. 汇总成 behavior_score
```

## 5 个子分与权重

```
behavior_score = 0.30 × coverage_pct
              + 0.25 × rule_compliance_pct
              + 0.20 × boundary_recognition_pct
              + 0.15 × script_used_pct
              + 0.10 × order_correctness_pct
```

### 子分 1：流程覆盖率 coverage_pct

```
coverage_pct = (合成任务 + 反例集 轨迹中出现的 unique step id 数) / (process.md 定义的 step 总数) × 100
```

- 合成任务应覆盖主流程的所有分支（构造原则见 05 号文档）
- 若 step 总数小（≤ 3），每 step 权重放大
- 子 agent 输出的 STEP 字段必须匹配 process.md 的 step id，否则不计入覆盖

### 子分 2：规则遵守率 rule_compliance_pct

```
rule_compliance_pct = (被正确遵守的 rule 数 / rules 总数) × 100
```

判定一条规则"被遵守"：

- 该规则的 `id` 出现在至少一个相关 step 的 `RULES_CHECKED` 列表里，且
- 对应 step 的 ACTION 或 OUTPUT 没有违反该规则的迹象

判定"违反"：

- 轨迹中某 step 的行为明显触犯了规则（如规则说"不得向用户展示原始数据"，但 OUTPUT 里暴露了）
- 该规则一次都没被 `RULES_CHECKED` 提及，且主 agent 能从轨迹推断出"这一步本该考虑它"

### 子分 3：边界识别率 boundary_recognition_pct

```
boundary_recognition_pct = (反例集中被正确处理的条目数 / 反例集总数) × 100
```

"正确处理"的 3 种合法响应：

1. 识别为不适用场景（跟用户说"这不是我该干的"）
2. 识别并命中对应规则，按规则要求的行为执行
3. 识别并命中对应踩坑，按踩坑提示的避免方法执行

"错误处理"：

- 按正常流程硬跑（没识别出这是边界）
- 识别但判错了方向（如把"不适用"当成"适用但要谨慎"）

### 子分 4：脚本真实调用率 script_used_pct

```
script_used_pct = (deterministic step 中轨迹 SCRIPT_USED=true 的数 / deterministic step 总数) × 100
```

**这是反"LLM 自己算"的关键指标**。子 agent C/D 必须通过调用 `python scripts/<name>.py` 完成 deterministic step，而不是 LLM 自己算。

双源交叉核对：
- 主来源：轨迹里的 `SCRIPT_USED: true`（子 agent 自报）
- 次来源：子 agent 的 Bash 工具调用历史（是否真的执行了 `python scripts/xxx.py`）

若两源矛盾（自报 true 但没 Bash 记录，或反之），按 Bash 记录为准，报告中附 `bypass_reason` 字段。

### 子分 5：流程顺序正确率 order_correctness_pct

```
order_correctness_pct = (按 process.md 顺序出现的 step 对数 / 相邻 step 对总数) × 100
```

实际等价于："有多少相邻步骤对是按定义顺序出现的"：

- 合成任务轨迹序列：`[step_1, step_2, step_4, step_3]`
- process.md 定义顺序：`step_1 → step_2 → step_3 → step_4`
- 对 `(step_2, step_4)` 这对是乱序，标 `out_of_order`
- 跳过某 step（step_3 被省略）本身不算乱序，但会体现在 coverage_pct 下降上

## spawn 子 agent C / D

### 子 agent C（合成任务）

```
prompt:
  你现在扮演一个加载了 {skill_name} 的助手。
  用户请求：{synthetic_task}

  你必须：
  - 只参考目标 skill 的文件（{skill_dir}/*）完成任务
  - 不能读评估器自身（…/linkfox-skill-evaluator/**）
  - 不能读 {skill_dir}/references/interview-record.md（访谈记录）
  - 不能读 {skill_dir}/.eval/ 下任何文件

  执行每一步时，输出一个 trace:step 块（格式见 07-trace-format.md）
  最后输出 trace:summary JSON 块
```

超时 10 分钟未完成 → 标 `skipped: timeout`，此条合成任务贡献的 coverage/rule 条目按 0 计入。

### 子 agent D（反例集）

反例集可能有 3-8 条。每条反例开一个**独立** spawn（避免前一条的上下文泄漏到下一条）：

```
prompt:
  你现在扮演一个加载了 {skill_name} 的助手。
  用户请求：{counter_example_scenario}

  按 skill 规则执行。按 trace 格式输出。
```

每条轨迹分别判定"正确处理"或"错误处理"。

## 主评估 agent 的核查流程

对每份轨迹：

1. 解析 `<!-- trace:step -->` 块 → list of steps
2. 解析末尾的 `<!-- trace:summary -->` JSON → 得到步骤 id 列表和脚本调用情况
3. 交叉核查：
   - step 序列 vs process.md：算 coverage、order
   - RULES_CHECKED vs rules 全集：算 rule_compliance
   - SCRIPT_USED vs deterministic step 集合：算 script_used
   - 对反例集轨迹：判定是否"正确处理"
4. 记录 `violations[]`：每条违反的 rule + 场景 + evidence 片段
5. 记录 `scripts_used[]`：列出所有 deterministic step 对应的脚本，标 invoked / bypassed + bypass_reason

## 输出结构

```yaml
behavior:
  score: 72
  coverage_pct: 85
  rule_compliance_pct: 80
  boundary_recognition_pct: 67
  script_used_pct: 100
  order_correctness_pct: 100
  synthetic_task: |
    某款 TWS 耳机，title 含 "Bluetooth Headphones Compatible with AirPods", brand 为 SonyBeats，品类 Electronics，价格 $29.99。
  counter_examples:
    - id: CE-1
      source: pitfall
      scenario: "title 写 'FDA Registered' 但不是真的 FDA 注册"
      expected: 触发 R4 虚假声明规则
      actual: skill 未识别，走了正常流程
      handled: false
    - id: CE-2
      source: boundary
      scenario: "用户传的 title 是品牌自家产品（品牌方自己卖），看起来像蹭品牌"
      expected: 识别为边界，不误判
      actual: 识别并跳过
      handled: true
  violations:
    - rule_id: R3
      step_id: step_4
      scenario: synthetic_main
      evidence: |
        trace:step 的 ACTION 中未触发品牌检查
      severity: high
  scripts_used:
    - script: scripts/check-brand-keywords.py
      invoked: true
      step_id: step_2
    - script: scripts/validate-title-length.py
      invoked: false
      bypass_reason: "轨迹显示 step_3 是 LLM 自己数的字数，未调脚本"
      step_id: step_3
  traces:
    synthetic_task: .eval/trace-20260427-1530.md#synthetic
    counter_examples: .eval/trace-20260427-1530.md#ce-1, #ce-2, ...
```

## 降级与失败模式

| 场景 | 处理 |
|------|------|
| 子 agent C/D 工具不可用 | 主 agent 不自己跑，直接标 `behavior: skipped`，overall_score 中 behavior 项算 0，advice 降级 |
| 子 agent 不输出 trace 格式 | 主 agent 尝试文本解析；仍失败则 behavior_score 按"仅计可解析部分" + 报告 `trace_parseability: partial` |
| 合成任务耗时 > 10 分钟 | 终止子 agent C，标 skipped；反例集仍尝试跑完（可能更快） |
| 反例集为空（skill 没有 boundaries/pitfalls） | boundary_recognition_pct 置 N/A，权重转嫁到其他子分按比例放大 |

## 避免的误区

- **别让主 agent 代跑任务**：spawn 子 agent 的意义就在独立执行。主 agent 下场自己按 skill 跑一遍等于"自评自改"，失去评估意义。
- **别在合成任务里埋提示词**：合成任务应该只写"用户说什么"，不应该告诉子 agent 应该调哪个脚本、查哪条规则。
- **别把反例当成测试用例**：反例是"看似合规的违规"，不是"语法错误"。单元测试式反例（如参数类型错）不在 E4 范围内（E3 已覆盖）。
