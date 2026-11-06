# 平台变量与凭据(认证信息)

> **什么时候读本文件**:用户要"存一个配置 / 改一个变量 / 建个凭据 / 这个流程用哪套认证",或者生成 / refine 的 flow 里要绑一个**已有凭据**时。`run` / `runs` / `history` / `automation` 不用读。
>
> 本文件对应脚本 `scripts/workflow_config.py`。生成 JSON 的节点契约仍以 `node-catalog.md` / `output-and-state.md` 为准,本文件只管"值存哪、怎么引用"。

## 0. 先分清三种存值的地方

| 要放的东西 | 放哪 | 为什么 |
| --- | --- | --- |
| 非敏感的全局配置(地区、阈值、模板) | 平台变量 `{{$vars.NAME}}` | 改值不用改 flow |
| 密钥 / token / 机器人地址 | **凭据**(credential) | 加密存储,按成员 / 租户隔离 |
| 本次执行的中间结果 | `$flow.state` 或 Node Output | 见 `output-and-state.md` |

一句话:**能公开的进变量,要保密的进凭据,过程数据进 state。**

## 1. 平台变量 `{{$vars.NAME}}`

### 语义

- 名称 → 值的平台级键值对。**任何 `acceptVariable: true` 的字段**都能写 `{{$vars.NAME}}`;沙箱节点的环境变量绑定(`customFunctionEnvVariables[].variableValue` / `customPythonFunctionEnvVariables[].variableValue`)也支持。
- 每次节点执行前解析,**查找范围是该 flow 属主的租户作用域**(见下);名字不存在时**模板原样保留**,不报错也不替换成空。所以"变量没建"的表现是字段里出现字面量 `{{$vars.X}}`,不是节点报错——落盘校验也不查变量表,别指望 `save_workflow.py` 拦住拼错的名字。
- 名字本身就是键:没有层级、没有默认值、没有类型系统。`type` 只有两种:
  - `static`(默认):值就是存的字符串;
  - `runtime`:运行时读**服务端进程**的环境变量(`process.env[NAME]`),不是读用户环境,也不是读你的本地 shell;**部署被判定为云平台时会直接拒绝创建 / 读取 `runtime` 变量**(返回 400 / 403),遇到就如实转述,不要改写成本地配置。
- 写 `$vars` 不需要在 flow 里声明;但 flow 引用了不存在的变量**不会让保存失败**(`save_workflow.py` 只校验 `{{ }}` 语法与 nodeId 存在,不校验变量表)。

### 作用域与可见性(必读,直接决定能放什么)

**运行时读取按 flow 属主的租户身份过滤**(2026-10-30 起,`groupId` + `memberId`;两边都没值的老数据落"空桶",空桶只对空桶可见):

1. **跨成员 / 跨租户同名不再冲突**。A 的 `LF_TOKEN` 与 B 的 `LF_TOKEN` 各读各的,名字本身不用再加前缀防撞;`REGION` 这种通用名在自己名下也不会被别人抢。
2. **同一作用域内同名仍然不行**。运行时按名字取,两条就只能报错:写入时服务端 **409**,批量导入自动加 ` (1)` 后缀,历史脏数据**只在被引用时**中止执行(没人引用的重复不影响任何流)。
3. **列表可见范围没变**:成员只看到自己的,组 OWNER 看到全组的。所以 OWNER 调 `vars list` 可能看到多个人各自同名的行——那是不同作用域,不是冲突;但也意味着 OWNER 改/删时容易改到别人那条(见下面 `set` / `delete` 的说明)。

**密钥仍然不要放变量**,理由换了,现在是这两条:

- `variable.value` **明文存库**(凭据是 `encryptedData`,加密的);
- 组 OWNER 能从变量列表看到组内**所有成员**的变量值,画布上的变量选择器也直接展示。

所以 token / 密钥 / 机器人地址 / 加签密钥一律进凭据。名字前缀现在只是可读性建议(`LF_REPORT_REGION` 比 `REGION` 好读),不再是防撞的必需手段。

### 脚本

```
python scripts/workflow_config.py vars list [--reveal]
python scripts/workflow_config.py vars set --name LF_REPORT_REGION --value-file -
python scripts/workflow_config.py vars delete --name LF_REPORT_REGION --confirm
python scripts/workflow_config.py vars delete --id <uuid> --confirm
```

- **值只从 `--value-file` 传**,`-` 表示 stdin;不要用命令行参数直接给值(会出现在进程列表里),也不要先写进 workspace 文件再回头看。推荐:

  ```
  python scripts/workflow_config.py vars set --name LF_REPORT_REGION --value-file - <<'EOF'
  US
  EOF
  ```

- `set` 按名字幂等:有则更新、无则创建。**同名命中多条时退出 65 并列出 id**,分两种情况:
  - 多条在**同一作用域**里——那是历史遗留脏数据,运行时会被中止,先 `delete --id` 清掉多余的;
  - 多条分属**不同成员**(你多半是组 OWNER,列表里能看到的别人的行)——脚本判不出哪条是你的,同样拒绝;`vars list` 看清 id 后用 `vars delete --id` / 在画布上改。
- `list` 默认脱敏(`value: "***"` + `valueState` + `valueLength`);`--reveal` 才打明文,**用户没明确要看就别加**。
- `delete` 不带 `--confirm` 只预览会删哪一条;删除会让引用它的 flow 读到字面量 `{{$vars.X}}`(不报错),回复里提醒一句。按名字删遇到多条同样要 `--id`。
- stdout 示例:

  ```json
  {"mode":"vars.set","action":"created","id":"<uuid>","name":"LF_REPORT_REGION","type":"static","valueLength":2,"warnings":[]}
  ```

- 退出码:0 成功;1 网络 / 鉴权 / 资源不存在;3 响应结构不是预期;64 用法错;65 服务端拒绝写操作(400 / 409);68 权限不足(403)。

## 2. 凭据(认证信息)

### 语义

- 一行凭据 = `name`(**类型**,如 `httpBearerToken`)+ `credentialName`(**显示名**,给人看)+ 加密后的字段值。
- 可见范围:成员只看得到自己的,组 owner 看得到全组的。别人的凭据 id 写进你的 flow,运行时取不到。
- **节点怎么绑**:`data.credential` 存的是**凭据实例 id**,不是类型名。生成时留 `""`;用户点名"用已有凭据 X"时先 `creds list` 拿 id,再写进节点。

### 类型与字段

| 类型 | 必填字段 | 可选 | 用在哪 |
| --- | --- | --- | --- |
| `linkfoxAgentApi` | `apiKey` | `baseUrl`(默认 `https://tool-gateway.linkfox.com`) | LinkfoxHTTP / DataReader / WriteFile / CrossBorderExpert / SendNotification / BusinessStart / ExecuteFlow。**后台自动绑定**,一般不手工建 |
| `httpBearerToken` | `token` | — | 原生 HTTP 节点(`Authorization: Bearer <token>`) |
| `httpApiKey` | `key`、`value` | — | 原生 HTTP 节点(自定义请求头) |
| `httpBasicAuth` | `basicAuthUsername`、`basicAuthPassword` | — | 原生 HTTP 节点(Basic) |

- HTTP 节点三种凭据都存在时的优先级:**basic → bearer → api-key**(按节点的实现顺序)。
- **模型凭据不在这里**:Agent / LLM 的模型凭据落在 `agentModelConfig.FLOWISE_CREDENTIAL_ID`,由用户在画布上选,`workflow_config.py` 不管、也不要拿它去查。
- `linkfoxAgentApi` 例外:上传时后台会自动绑定(workflow-studio 的 `SkillUploadDefaultsFiller`),所以生成 / 补配置都不提它;只有用户明确说"自动绑定不好使,帮我手工建一份"时才 `creds create`。

### 脚本

```
python scripts/workflow_config.py creds list [--type httpBearerToken]
python scripts/workflow_config.py creds create --type httpBearerToken --credential-name 飞书Token --data-file -
python scripts/workflow_config.py creds update --id <uuid> --data-file -
python scripts/workflow_config.py creds delete --id <uuid> --confirm
```

- 值只从 `--data-file`(或 stdin `-`)进来;脚本**不回显值**,stdout 只给 `id` / 类型 / 显示名 / 字段名。
- `create` 会按类型校验必填字段(缺了退出 64),不认识的字段只警告;`update` 是服务端 merge 语义,**只传要改的字段**,脚本会先查这条凭据的类型一并提交,避免把类型冲掉。
- **不调** `GET /credentials/:id` 和 `/credentials/:id/reveal`——那两个会回解密后的内容。用户想看明文,让他去画布上看。
- **创建只在用户明确要求、且值是他本轮亲手给的时候跑**。密钥不落 workspace 文件、不写进 memory、不贴回回复。
- `delete` 不带 `--confirm` 只预览;回复里提醒"引用它的流运行时会取不到认证".
- `creds list` 只返回元数据,可以随时跑;要绑凭据时先 list 再让用户挑(别凭显示名猜 id)。**别人分享(share)给你的凭据不在 list 里**,`update` / `delete` 也会报"找不到"——那种情况让用户去画布上改。

## 3. 调接口的认证(脚本自己用的那套)

服务端有三档认证,作用在各接口上:

| 档 | 触发 | 本 skill 是否使用 |
| --- | --- | --- |
| 白名单(免鉴权) | 健康检查、prediction、webhook、上传文件等 | 只用 prediction 之外不需要 |
| **API Key 或登录态(默认)** | 其余接口 | **只用 API Key**(env `LINKFOX_AGENT_API_KEY`) |
| 仅登录(黑名单) | `/api/v1/workspace*`、`/organizationuser*`、`/files*`、`/nvidia-nim*` | 不用,也不在能力边界内 |

- 地址只来自 `linkfox_paths.get_api_base()`(env `LINKFOX_TOOL_GATEWAY`,缺省正式网关),不硬编码、不另立环境变量。
- 不碰登录态 JWT / cookie,也不用任何系统内部 API Key。
- 可调:`/api/v1/chatflows*`、`/api/v1/prediction`、`/api/v1/executions*`、`/api/v1/variables*`、`/api/v1/credentials*`。
- 401 / 403 排查:401 多半是 key 类型不对或值带引号 / 空格(`scripts/workflow_auth.py` 会追加提示);403 多半是这把 Key 绑定的角色缺权限位(`variables:*` / `credentials:*`)或租户 / 分组范围不对,不是脚本 bug,如实转述即可。

## 4. 和生成 / refine 的配合

1. 需求里出现"存个配置 / 改个变量 / 换个 token / 换个 webhook 地址"时:非敏感进变量,密钥进凭据。拿不准就问一句。
2. flow 要引用变量:在 `acceptVariable` 字段里写 `{{$vars.NAME}}`,并说明"变量不存在时字段里会留字面量,不报错"。
3. flow 要绑已有凭据:`creds list` → 按类型 + 显示名选中 → 把 id 写进 `data.credential`(或 `inputs.FLOWISE_CREDENTIAL_ID`)。
4. 补配置指引里按实际节点点名要配的变量名 / 凭据显示名;**不要**提示用户绑 `linkfoxAgentApi`。

## 5. 检查清单

- [ ] 密钥没进变量;真写了的话回复里已说明"变量明文存库 + 组 OWNER 可见",并建议改用凭据。
- [ ] 变量名是给人看的;不再为"防跨租户撞名"加前缀(已按租户隔离),但通用名仍建议加业务前缀提升可读性。
- [ ] 遇到同名多条(退出 65)时没硬覆盖:说清是同作用域脏数据还是不同成员的同名行,让用户选 `--id`。
- [ ] `vars set` 的值走 `--value-file -`,命令行里没有明文。
- [ ] 凭据创建只在用户明确要求时发生,值来自用户本轮,没有被写进 workspace 文件或 memory。
- [ ] 回复里没有出现凭据值或变量明文(除非用户明确要求 `--reveal`)。
- [ ] `delete` 都带了 `--confirm`,且回复里说了删掉会影响谁。
