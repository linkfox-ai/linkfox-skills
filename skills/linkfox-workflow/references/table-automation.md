# 工作流 ↔ 多维表关联(记录触发 / 定时任务的订阅)

一条关联(下称「订阅」)= **哪个工作流**,挂在**哪本多维表的哪张数据表**上,被**哪种记录事件**触发。
订阅生效后,多维表记录变更 → 按表反查订阅 → 命中则调用该工作流。对外接口原文见仓库 `docs/WORKFLOW-TABLE-BINDING-API.md`;本文件只讲 agent 怎么用。

订阅分两类:

| 类型 | `eventType` | 谁来跑 | 关联的作用 |
| --- | --- | --- | --- |
| 记录触发 | `recordCreated` / `recordUpdated` / `recordConditionMet` | 收到记录变更事件后调用 | 登记触发表,让那张表外推记录变更 |
| 定时任务 | `schedule` | Flowise 调度器按排期跑 | 只记"这条流挂在哪本多维表 / 哪张表下"(侧栏可见、权限闸门可判);**不登记触发表,记录变更不会触发它**。见 §1.5 |

| 要做的事 | 走哪条路 |
| --- | --- |
| 新建 / 修改记录触发(换表、换事件、改条件、改监听字段) | **方式 A**:照常 save + upload,看 stdout 的 `tableAutomation` |
| 不动画布地**启用 / 停用**自动化 | **方式 B**:`table_automation.py set --enabled true\|false` |
| "这条流的自动化在不在 / 开着没" | `table_automation.py list --workflow-id <id>` |
| "这张表挂了哪些工作流" | `table_automation.py by-notebook --notebook-id <nbk> --table-id <tbl>` |

**不要用 `linkfox-smart-table` 的 `registerWorkflow` / `updateWorkflowTriggerTable` / `unregisterWorkflow`**:那三个只改多维表侧的关联,不写订阅行,两边会对不上(多维表推了事件、却查不到订阅,或者反过来)。

## 1. 方式 A:上传即关联

`upload_workflow.py` 调的 `POST/PUT /api/v1/chatflows` 本身就会按开始节点登记订阅,**不需要用户再去界面上保存一次**。结果在 stdout 的 `tableAutomation`:

```json
"tableAutomation": {"status": "REGISTERED", "effective": true, "meaning": "...", "notebookId": "nbk…", "tableId": "tbl…"}
```

| `status` | `effective` | 含义 | 回复里怎么说 |
| --- | --- | --- | --- |
| `REGISTERED` | true | 首次登记成功 | "已关联到「<多维表>/<数据表>」,表里<事件>时会自动运行" |
| `UPDATED` | true | 已登记过,触发配置已更新 | 同上,"触发配置已更新" |
| `REASSIGNED` | true | 从另一本多维表换挂过来 | 同上,点明换了多维表 |
| `UNBOUND` | true | 记录触发:触发表已解绑;**定时任务:再次保存的正常结果**(stdout 带 `eventType: "schedule"`) | 记录触发:"已停用,表里变更不再触发";定时任务:"定时任务挂在「<表>」下",**不要**说成停用 |
| `disabled` | true | 开始节点不再是记录触发(也不是挂在多维表下的定时启动),订阅已停用 | **必须提醒**:"原来挂在「<表>」上的自动触发 / 定时任务已经从这张表下摘掉了" |
| `SKIPPED_NO_NOTEBOOK` | false | 没带 `notebookId`,无处登记 | "工作流已保存,但**自动化没生效**":补 `notebookId` 后重传 |
| `FAILED` | false | 多维表侧登记失败 | "已保存,但自动化没生效";重试 = 原样再上传一次(幂等) |
| `notSaved` | false | 服务端校验没过 | "已保存,但自动化没生效";检查开始节点的事件 / 条件配置 |
| 其他 | false | 认不出的新状态 | 照"没生效"说,不替用户说已生效 |
| `""` | **null** | 开始节点是记录触发,但服务端没回关联结果 | 说"没拿到关联结果",跑一次 `table_automation.py list --workflow-id <id>` 再下结论 |

- **字段不出现 = 这次保存与多维表无关**(开始节点既不是记录触发,也不是带 `linkfoxTableAutomationContext` 的定时启动,也不是从这两者切走),回复里不提自动化。
- `effective=false` **不算上传失败**:退出码仍是 0、照常输出 `<linkfox-flow-info>`,但回复第一段就要说"自动化没生效",不能只报"已上传"。stderr 会多一行 `WARNING: 工作流已保存,但多维表自动化未生效`。
- "已关联"≠"已经跑过"。有没有真的被触发,以执行记录为准(`runs`)。
- PUT 不带 `flowData`(只改名)订阅不动;本 skill 的上传永远带 `flowData`,所以每次上传都会按当前开始节点重算订阅。

## 1.5 定时任务挂到多维表下

Start 配成「按业务时间启动」(`startInputType=scheduleInput`)时,**排期**和**关联**是两件事:排期(几点跑)由 Flowise 按 `schedule*` 字段管;关联(挂在哪张表下)看 Start 上的 `linkfoxTableAutomationContext`。**不带它 = 普通定时流,不建立关联**。

```json
"inputs": {
    "startInputType": "scheduleInput",
    "scheduleType": "visualPicker",
    "scheduleFrequency": "daily",
    "scheduleOnTime": "09:00",
    "scheduleTimezone": "Asia/Shanghai",
    "linkfoxTableAutomationContext": {"notebookId": "nbk…", "tableId": "tbl…"}
}
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `notebookId` | ✅ | 多维表格容器 id(散表 `__loose__`)。**缺了就当没挂表** |
| `tableId` | 强烈建议 | 真实 `tbl…`。不带 / 形状不对 ⇒ 服务端存成占位 `tbl__schedule__`,侧栏归不到具体表、权限闸门也不探(stdout 会带 `tableIdPlaceholder`) |
| `entryPoint` | | 不写。`operations_center` 只给运营流程中心入口用 |

**什么时候带**:

- 用户说"挂到这张表下 / 在表格自动化里能看到"时带,表按「选表」规则选定。
- 定时流读 / 写的是**同一张**多维表(`DataReader` / `WriteFile` 指向它)时默认带上这张表,在方案里点一句"会挂在「<表>」的自动化下";涉及多张表又说不清挂哪张时问一次。
- 跟多维表无关的定时流不带。
- **id 写在上下文对象里,不是 Start 上记录触发那组 `notebookId` / `tableId`**(切到定时时会被显示条件清掉,写了也没用)。`save_workflow.py` 对缺 `notebookId` / 缺 `tableId` 给 warning,`tableId` 填成 `nbk…` 直接 error。
- refine 存量定时流:上下文属于开始节点 `inputs`,开始节点锁定照旧。用户本轮明确要"挂到 / 换到某张表下"才写完整开始节点 inputs、带 `--allow-trigger-change`。

**回报**(仍看 stdout 的 `tableAutomation`):首次保存 `REGISTERED`;**再次保存 `UNBOUND` 是正常成功**(定时流登记的触发表恒为空,不是被停用);换到另一本多维表 `REASSIGNED`,第二步失败回 `FAILED` = 暂时不挂在任何多维表下,原样再上传一次;去掉上下文 / 缺 `notebookId` 且之前有订阅 ⇒ `disabled`。

**行为边界**:

- 记录变更**不会**触发定时流;"表里一改就跑"要的是记录触发,不是这个。
- 定时流跑不跑由 Flowise 的排期开关管(画布顶部开关),**与订阅的 `enabled` 无关**。所以 `table_automation.py set` 对定时任务一律拒绝(退出 66):停用订阅只会让它从侧栏消失、照样按点跑。用户要"停掉这个定时任务"时,告诉他们在画布顶部关掉开关;要彻底不再定时,refine 开始节点改成手动启动。
- 保存一次有效配置就会重新启用排期:refine 上传后,原来被用户关掉的定时可能又开了,回复里提一句。
- 多维表移进回收站会暂停排期、恢复时再打开(平台行为,不由本 skill 处理)。

### 保存被拒

| 报错 | 含义 | 怎么办 |
| --- | --- | --- |
| `no_table_permission` | 当前账号对触发表无权限 | 让用户换一张有编辑权限的表(重新走「选表」) |
| `read_only_workflow` | 这个工作流对当前账号只读 | 如实告诉用户,不要换 workflowId 另建一份 |
| `status 409` / 已被别的成员绑定 | 订阅属于别人,只有绑定人能改触发 | 如实转述;不要换 workflowId 绕过 |
| `tenant has no member mapping` | 租户映射缺失 | 平台侧问题,重试无效 |

## 2. 字段名和字段 ID 都写

监听字段 / 条件字段**按名字和 ID 各存一份**。只写名字时,用户在表里改列名后订阅会**静默失效**(事件照来、匹配不上、不跑)。

| BusinessStart `inputs` | 类型 | 说明 |
| --- | --- | --- |
| `recordWatchFieldNames` | string[] | 监听字段名,仅 `recordUpdated`;空 = 任意字段修改都触发 |
| `recordWatchFieldIds` | string[] | 对应的字段 ID(`fld…`),顺序与名字一致 |
| `recordConditionFieldName` | string | 条件字段名,仅 `recordConditionMet` |
| `recordConditionFieldId` | **string[]** | 条件字段 ID,**是数组**,只取第一项:`["fldStage00001"]` |

字段 ID 来自 `linkfox-smart-table` 的 `listFields` 出参 `fields[].fieldId`(选表后本来就要调它拿真表头)。多值字段写真数组或 JSON 字符串都认。

- **新生成**:名字和 ID 一起写。`save_workflow.py` 对"只有名字没有 ID"给 warning,ID 不以 `fld` 开头直接 error。
- **refine 存量流程**:基线没有 ID 时,开始节点锁定照旧,**不要顺手补**。在回复里问一句"要不要顺便补上字段 ID,防止改列名后失效";用户同意才在片段里写完整开始节点 inputs、带 `--allow-trigger-change`。
- `table_automation.py` **不接受手填字段 ID**:订阅从画布推导,只在订阅里补 ID,下次画布保存又会被覆盖回去。补 ID 只能走 refine。

### 事件与条件(save 时校验)

| `recordEventType` | 附加配置 |
| --- | --- |
| `recordCreated` | 无 |
| `recordUpdated` | 监听字段(可选) |
| `recordConditionMet` | 条件字段 + 算子 + 值 |
| `recordTimeReached` | **暂不支持**,save 直接 error |

算子:`equal` / `notEqual` / `contains` / `notContains` / `isGreater` / `isLess` / `isEmpty` / `notEmpty`。`isEmpty` / `notEmpty` 不带值,其余必须带值(空串视为未填,会 `notSaved`)。`recordCheckIntervalMinutes` 必须是正整数。

## 3. 方式 B:`table_automation.py`

```bash
python scripts/table_automation.py list [--workflow-id <id>] [--table-id tbl…] [--event-type <t>|schedule] [--enabled true|false]
python scripts/table_automation.py by-notebook --notebook-id nbk…|__loose__ [--table-id tbl…]
python scripts/table_automation.py set --workflow-id <id> --enabled true|false [--dry-run]
```

### `set`:启用 / 停用

- **只管记录触发**。开始节点是带上下文的定时启动、或现有订阅是 `eventType=schedule` 时,退出 66,理由见 §1.5。
- 请求体**从服务端那条 flow 的开始节点推导**(`source: "canvas"`),画布字段名 → 接口字段名的转换由脚本做,不要手写 curl。开始节点已不是记录触发时,停用会退到现有订阅行(`source: "existingSubscription"`)。
- `--enabled` **必填**。接口不带 `enabled` 会被当成启用,所以脚本永远显式发。
- 停用不删行,多维表侧解绑,结果 `UNBOUND`。**没有 DELETE**。
- 只在用户明确说"停用 / 关掉 / 暂停这个自动化""重新打开 / 启用"时跑;它是可逆的,用户原话就是授权,不需要另外确认。拿不准用户指的是哪条流就先 `list` 让用户选。
- **停用的保持期**:之后任何一次 refine 上传都会按开始节点重算订阅,可能把它重新打开。停用后的流程再被 refine 时,上传完跑一次 `list --workflow-id <id>`。如果被重新启用,告诉用户并问要不要再停一次。
- 要停用、但用户其实是想**换触发方式**的,走 refine(改开始节点 + `--allow-trigger-change`),上传后的 `disabled` 状态已经包含停用。

| 退出码 | 含义 | 回复 |
| --- | --- | --- |
| 0 | 已生效,看 `tableSync.status` | 按 §1 的话术 |
| 66 | 推不出订阅:不是记录触发也没有旧订阅;或配置不完整(缺 notebookId / 条件);或想重新启用一条画布已经切走的旧订阅;或这是定时任务 | 转述 stderr;要恢复记录触发就走 refine;定时任务按 §1.5 引导到画布顶部开关 |
| 68 | 409 已被别的成员绑定 / 403 对触发表无权限 | 如实转述,不绕过 |
| 70 | 请求成功,多维表侧没登记上(`FAILED` / `SKIPPED_NO_NOTEBOOK` …) | "订阅已保存,但自动化没生效",stdout 的 `tableSync.detail` 原样转述;`FAILED` 可原样重跑一次 |

### `list` / `by-notebook`:查看

- `list` 只看得到**自己创建的**订阅;`--workflow-id` 在客户端过滤。空列表 = 自己名下没有这条订阅,**不等于**这条流没有自动化(可能是别人绑的)。
- `by-notebook` 不带 `--table-id` 只回自己的;带了会按调用者对该表的权限放宽到**所有人**的订阅(含同容器其他表)。带了却回空,`scope` 会说"可能没有,也可能无权限",不要说成"这张表没挂任何工作流"。
- `eventType=schedule` 的行是挂在该表下的定时任务,汇总时说"定时任务",它的 `enabled` 不代表排期开没开。
- 每行的 `watchFieldIdsMissing` / `conditionFieldIdMissing` 为 true 时,顺带提醒用户改列名会失效。
- 完整响应落盘(`path`),stdout 只有摘要;用中文业务语言汇总(哪条流、哪张表、什么事件、开着没),不贴 JSON。

## 4. 边界

- 不删 flow,所以"删工作流前先停用"不涉及本 skill;用户要删流程时,提醒他们先说一句"停用这个自动化",否则那张表会继续推送没人消费的事件。
- 方式 B 不产出 JSON、不落盘 workflow、不跑 save/upload、不输出 `<linkfox-flow-info>`(画布内容没变)。
- 分享页的 `X-Tea-Base-Share` / `X-Tea-Share-Token` 不由 agent 传。
