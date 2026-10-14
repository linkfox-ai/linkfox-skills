# 历史版本(`history`)

服务端在工作流的「历史记录」开关打开后,**每次保存自动记一版**:谁改的、改了哪些节点、当时的整张画布。本 skill 上传时会顺手把开关打开,所以经本 skill 建的、改的流都有历史。

这一节管三件事:上传后怎么报版本号、用户问历史时怎么查、用户要撤销时怎么还原。

## 1. 上传时:开关与版本号(自动,不用你调)

`upload_workflow.py` 的 stdout 多一个 `history` 字段:

| 字段 | 含义 |
| --- | --- |
| `enabled` | 历史记录现在开没开。`null` = 没问出来(老服务端 / 网络失败) |
| `status` | `recorded` 这次新记了一版;`unchanged` 内容和最新一版一样,没新记;`disabled` 开关关着;`failed` 写历史失败;`forbidden` 不是属主,打不开;`unsupported` 服务端还没有历史接口;`error` 网络失败 |
| `version` | 这次上传后,当前内容是第几版 |
| `previousVersion` | 只在 `updated` + `recorded` 时有:改之前那一版。**撤销就还原到它** |
| `enableForbidden` | 开关关着且当前调用者不是属主,打不开 |

**`history` 任何状态都不影响上传成功的判定**,判定仍只看 `workflowId` + `mappingStatus=saved` + 退出码 0。

回复里怎么说(放在"下一步"指引之后、flow info 标签之前,一句话):

- `updated` 且有 `previousVersion`:「这次修改记为第 {version} 版;想撤销可以说"撤销刚才的修改",会还原到第 {previousVersion} 版。」
- `created` 且有 `version`:「已开启历史记录,当前是第 {version} 版。」
- `unchanged`:不提版本(内容没变)。
- `forbidden` / `enableForbidden`:「这个流程的历史记录没开,只有创建者能打开,所以这次修改无法一键撤销。」
- 其它(`failed` / `error` / `unsupported` / `null`):不提。

不要为了拿版本号另跑 `workflow_history.py list`:stdout 里的 `version` 就是这次保存那一版,事后查列表可能撞上别人同时保存。

## 2. 查看:`list` / `show` / `diff`(纯读,不需要确认)

```
python scripts/workflow_history.py list --workflow-id <id> [--limit 10]
python scripts/workflow_history.py show --workflow-id <id> --version <N>
python scripts/workflow_history.py diff --workflow-id <id> --from <N> --to <M>
```

- `list` 按版本倒序。每条有 `version` / `changeText`(开启历史记录 / 修改了工作流 / 修改了配置 / 还原到第 N 版)/ `changedBy` / `createdDate` / `change`(新增 / 删除 / 修改了哪些节点,修改的带参数名)。
- `diff` 不要求相邻,方向是 from → to。
- 服务端**只给改了哪个参数,不给新旧值**(参数里可能有密钥)。用户要看具体值时用 `show` 两版,读落盘的快照文件自己比,只转述非敏感字段。
- 退出 67:这个流程没开历史,也没有任何版本。直说"这个流程还没有历史记录",并说明创建者下次经对话修改时会自动打开。

回复用中文业务语言:"第 7 版 · 小王 · 10-09 14:12 · 修改了「总结」节点的提示词"。不贴 JSON,不贴路径,`total` 和 `returned` 别混。

## 3. 还原:`restore`(写操作,两步走)

用户说"撤销刚才的修改 / 回到第 3 版 / 恢复成昨天那版"时:

1. **定位目标版本,同时记下"你以为的最新版"**。
   - "撤销刚才的修改":目标 = 上一轮 `upload_workflow.py` 的 `history.previousVersion`,以为的最新版 = 同一轮的 `history.version`。
   - 对话里找不到这两个数(新会话、上下文被压缩、上一轮没报版本):先 `list` 一次,把最近几版列给用户选,**不猜哪一版是"刚才"**。
   - "回到第 3 版"这类明确版本号:目标就是它;以为的最新版取你最近一次 `list` 或预览看到的 `latestVersion`,没看过就先 `list`。
   - "昨天那版"对不上唯一版本时,列出候选让用户选。
2. **预览**(不带 `--confirm`,不写任何东西),**必须带 `--expect-latest`**:

   ```
   python scripts/workflow_history.py restore --workflow-id <id> --version <目标> --expect-latest <以为的最新版>
   ```

   - **退出 69 = 之后又有人保存过**。stdout 的 `newerVersions` 列出第 N 版之后的每一版(变更人、时间、改了哪些节点)。不要还原,先把这些转述给用户并问:"在 AI 修改之后,{变更人} 又改了 {节点}。要一起撤掉(还原到第 {目标} 版),还是只撤 AI 那次?" 只撤 AI 那次不能用还原做到,要走 `refine`:在当前基线上把 AI 那次的改动反着改回去。用户选"一起撤掉"后,用 stdout 的 `latestVersion` 作为新的 `--expect-latest` 重新预览。`newerTruncated: true` 时说明还有更多,建议用户到画布的「历史记录」里看。
   - 通过时,stdout 的 `willChange` 是"当前最新版 → 目标版"会改回的节点。把它转述给用户,并说明:**整张画布会被替换,当前未保存的画布改动会丢**;还原本身会记成新的一版,还原错了还能再还原回去。
3. **用户明确同意后**才带 `--confirm`,`--expect-latest` 用**预览 stdout 里的 `latestVersion`**:

   ```
   python scripts/workflow_history.py restore --workflow-id <id> --version <目标> --expect-latest <预览时的 latestVersion> --confirm
   ```

   `--confirm` 不带 `--expect-latest` 会直接退出 64:用户同意的是预览里那份改动,预览之后有人又存过,实际撤掉的就不止这些。这时退出 69,按上面重新问。

   用户本轮原话就是"撤销到第 3 版,直接做"这种明确指令时,预览和确认可以同一轮做完,但回复里仍要说清改回了哪些节点;预览退出 69 时照样停下来问。

规则:

- **只有属主能还原**。预览阶段就会检查,协作者退出 68,告诉用户"只有创建者可以还原,请让创建者在画布的「历史记录」里操作"。不要改用 `--restore-from` 或手工重放 JSON 绕过 —— 那等于协作者越权还原。
- 退出 68 + 409:有人在确认与写入之间的几秒内保存过。重新预览一次再问用户,不自动重试。
- 退出 69 不是错误,是"之后又有人改过"的提醒;**不许为了过检查把 `--expect-latest` 改成服务端的最新值后直接 `--confirm`**,必须先让用户看到 `newerVersions` 并作出选择。
- 还原成功后不贴 JSON,报"已还原到第 N 版,记为第 M 版(`newVersion`)",**最后一行输出 `<linkfox-flow-info id="<workflowId>"></linkfox-flow-info>`**。前台画布只在新标签出现时重新拉取;不输出它,画布停在旧内容上,用户再点保存就把还原冲掉了。只预览、或还原失败(退出非 0)时不输出标签。
- 还原后本地基线自动作废:下一轮 refine 照常先 fetch,不用你处理。
- 多维表记录触发的流:服务端会按还原出来的触发配置同步订阅,和正常保存一样,不用额外操作。

## 和本地快照(`--restore-from`)的区别

| | 服务端历史(本节) | 本地快照 `save_workflow.py --restore-from` |
| --- | --- | --- |
| 用途 | 用户要撤销 / 回到某个历史版本 | 只用于**临时测试版的恢复**(见 `runtime-execution.md`) |
| 谁能用 | 只有属主 | 任何能上传的人 |
| 版本来源 | 每次保存(含画布上人手改的) | 只有本 skill fetch 过的那几次,最多 5 份 |

用户说"撤销 / 回滚 / 回到第 N 版"时一律走服务端历史;本地快照不出现在给用户的话术里。
