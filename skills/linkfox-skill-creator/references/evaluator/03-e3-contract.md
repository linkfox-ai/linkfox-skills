# 03 E3 契约符合

回答一个问题：**skill 的文件结构、frontmatter、脚本化契约是否符合规范？**

这是 hard gate 的第一关。**任一 check fail → E3 fail → 整个评估终止**。

## 执行方式

**不由本 skill 直接实现**，而是调用 CLI 内置 linter：

```bash
linkfoxskill skill lint <skill-name> --json
```

返回 JSON：

```json
{
  "passed": true,
  "skill_name": "linkfox-amazon-listing-infringement-check",
  "checks_total": 10,
  "checks_passed": 10,
  "issues": []
}
```

失败返回：

```json
{
  "passed": false,
  "skill_name": "...",
  "checks_total": 10,
  "checks_passed": 7,
  "issues": [
    {
      "check_id": "C1",
      "check_name": "SKILL.md frontmatter 合法",
      "severity": "error",
      "file": "SKILL.md",
      "line": 3,
      "message": "description 字段少于 50 字"
    }
  ]
}
```

主评估 agent **直接采用** linter 输出，不做二次判断。

## 10 项契约检查（对齐 CLI linter）

| ID | 名称 | 检查内容 |
|----|------|---------|
| C1 | frontmatter 合法 | `name` 存在且以 `linkfox-` 开头（kebab-case）；`description` 非空且 ≥ 50 字；frontmatter 本身可解析 |
| C2 | SKILL.md ≤ 200 行 | 整个文件行数（含 frontmatter）≤ 200 |
| C3 | interview-record 存在且 schema 合法 | `references/interview-record.md` 存在；frontmatter `schema_version: 1`；必要字段 scenario/inputs/process/rules/boundaries 存在 |
| C4 | references 无孤儿 | `references/*.md` 中每个文件都被 SKILL.md 或其他 reference 显式引用（路径字符串匹配） |
| C5 | deterministic → script 存在 | interview-record.md 的 `process[]` 中所有 `deterministic: true` 的步骤，对应 `scripts/<name>.py` 必须存在 |
| C6 | scripts 无孤儿 | `scripts/*.py` 中每个文件都在 SKILL.md 或 workflow.md 中被引用 |
| C7 | script docstring 非空 | 每个 `scripts/*.py` 的模块级 docstring 非空 |
| C8 | requirements.txt 可解析 | 若存在 `scripts/requirements.txt`，能被 pip 合法解析（每行 `pkg==x.y.z` 或 `pkg>=x.y.z` 等合法格式） |
| C9 | 无无关杂项 | 不含 `desktop.ini` / `.DS_Store` / `Thumbs.db` / `*.tmp` / `*.bak` / `.linkfox-bak`（后者是 hint 系统的备份，不应出现在 skill 目录里） |
| C10 | frontmatter 元字段 | `authored_by: linkfox-skill-creator`；`interview_record` 字段指向 `references/interview-record.md` |

## 严重度

所有 C1-C10 的 issue 都是 `error`（fail 即 fail），没有 warning 级别。

但在报告的 `recommended_fixes` 中，按影响程度给排序提示：

1. C1, C3, C10 — 元数据/入口层面：**必须最先修**
2. C5 — 脚本化契约：影响 E4 能否跑
3. C2 — SKILL.md 超长：影响 E2 读取效率
4. C4, C6 — 孤儿文件：影响可维护性
5. C7, C8, C9 — 清洁度

## 与 E4 的联动

- C5 fail 直接导致 E4 无法跑合成任务（`scripts/` 缺失）
- C6 的孤儿脚本在 E4 中会被发现（子 agent C/D 执行轨迹里不会调用它）——但 C6 本身是静态检查，在 E3 就能发现

## 与 linter 的版本对齐

- E3 check 的 ID / 名称 / 判定逻辑必须与 CLI `src/lib/skill-linter.js` 一致
- linter 升级时（如增加 C11），本文档同步更新
- Evaluator 不允许在 E3 中"额外"追加自己的契约检查——会导致"CLI 通过但 Evaluator fail"的双 source 矛盾

## 降级场景

若 CLI 不可用（未安装 / 版本过旧 / 报错）：

- 主评估 agent **不得**自己写一套 C1-C10
- 应告知用户"当前环境 CLI linter 不可用，E3 无法评估，请 `npm i -g @linkfox/skills-cli` 后重试"
- 整个评估终止，不进入 E2

## 输出结构

```yaml
contract:
  passed: true
  checks_total: 10
  checks_passed: 10
  issues: []
  # 或 fail 时：
  # passed: false
  # checks_passed: 7
  # issues:
  #   - check_id: C1
  #     check_name: "frontmatter 合法"
  #     severity: error
  #     file: SKILL.md
  #     line: 3
  #     message: "description 字段少于 50 字"
```

## 边界

- 若 skill 不是由 Creator 生成（`authored_by` ≠ `linkfox-skill-creator`，C10 fail）：
  - E3 仍然 fail，终止评估
  - 报告提示"本 skill 非 Creator 产出，无法完成完整评估。仅契约部分可用。"
  - 可以单独给用户展示 `skill lint` 结果，但不写正式 `.eval/report-*.md`
