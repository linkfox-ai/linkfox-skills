# 品牌基因提取：素材上传凭证接口说明

本技能的视觉推理由下游 textgen 完成；本文件只定义本技能内置上传器使用的 LinkFox 服务接口。以下字段说明描述上传器的请求、校验与响应处理；服务端可选限制以实际返回为准。

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 接口：获取 OSS 临时上传凭证

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/getStsVoucherByAPI`

### 请求参数

| 参数 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| 请求体 | object | 是 | 空 JSON 对象 `{}`；接口不接受业务入参。 |

#### 脚本与上传限制

| 参数 / 约定 | 类型 | 必填 | 默认值、限制与说明 |
|---|---|---|---|
| get_upload_voucher.py params | JSON 字符串 | 否 | 默认 `{}`，只接受空对象。直接运行仅展示脱敏响应，不导出可重用的密钥文件。 |
| --inline | CLI flag | 否 | 展示完整脱敏响应；不解除凭证保护。 |
| --no-cache | CLI flag | 否 | 上传凭证无响应缓存；业务封装调用 `call_api.run` 时强制加入，不读写凭证缓存，并在业务层跳过公共调用器创建缓存目录的副作用，当前目录只读时回退到其他可写根目录。 |
| upload_files.py paths | 文件路径列表 | 是 | `python scripts/upload_files.py <文件> [<文件> ...]`；保留顺序，路径不存在时记录失败，不消耗上传次数。`--help` 只显示本地帮助。 |
| LINKFOX_TOOL_GATEWAY | string | 否 | 默认公共基础地址；去除尾部 `/`。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string | 是，二选一 | 主变量优先，兼容备用变量；缺少时在请求前报错。 |
| 请求重试 | integer | 否 | 最多尝试 3 次，等待 1 秒、2 秒；仅 HTTP 408/429/500/502/503/504 及连接或 JSON 解析异常重试。其他 HTTP 错误立即失败，业务错误不重试。 |
| 凭证复用 | object | 否 | 同一批次的成功文件复用内存凭证；单文件处理异常后清空，后续未处理项可重新获取，已成功项不重复上传。不是跨请求响应缓存。 |
| supportedTypes | string | 服务端可选 | 按逗号拆分、去空白、转小写后检查扩展名；服务端为空时不臆造白名单。白名单参考值为 `xlsx,csv,jpg,jpeg,webp,png,pdf,zip,json,md,mp4`，实际以服务端返回为准，不硬编码。 |
| maxFileSize | integer / 数字字符串 | 服务端可选 | 正整数按字节限制单文件；数字字符串先转 integer。单文件上限参考值为 50 MB，实际以服务端返回为准，不作为缺省限制。 |
| maxFileCount | integer / 数字字符串 | 服务端可选 | 正整数限制批次实际上传尝试次数；首次确定后整批沿用，失败尝试也计数。单批次数参考值为 10 个，实际以服务端返回为准，不作为缺省限制。 |
| oss2 | Python 依赖 | 上传时是 | 缺少时明确提示用户或环境管理员运行 `python -m pip install oss2`；不擅自安装或修改环境。凭证诊断不需要此依赖。 |
| 源文件 | 文件 | 是 | 仅上传，不转码、压缩、裁剪或改写。敏感或私密内容不得上传，必须先取得用户对公开可访问 URL 的确认。 |
| 文件类型建议 | string | 否 | `txt/html/docx` 不在上述参考白名单中；纯文本优先 `.md`，Excel 可直接打开的内容用 `.xlsx`，不要用无 BOM 的 CSV。最终以服务端限制为准。 |
| Content-Type | string | 否 | md=`text/markdown; charset=utf-8`；txt=`text/plain; charset=utf-8`；csv=`text/csv; charset=utf-8`；json=`application/json; charset=utf-8`；html=`text/html; charset=utf-8`；webp=`image/webp`。其他扩展名不额外声明；该映射不表示白名单放行。charset 只在 HTTP 响应头中，下载后仍由编辑器判断编码。 |

上传对象名采用 `dir`（缺省 `tmp`）/年份/月/随机十六进制串.扩展名。扩展名转小写，无扩展名用 `bin`。OSS endpoint 缺少协议时补 `https://`，去除尾部 `/`；结果地址为 `https://<bucketName>.<endpoint主机>/<object_key>`。

### 响应结构

#### 网关与凭证字段

| 字段 | 类型 | 必需性与说明 |
|---|---|---|
| errcode | number / string / null | 可选；按公共响应码规则判断，不将 0 或 false 当作缺省成功。 |
| errmsg | string | 可选；网关业务消息。 |
| message | string | 可选；上传器兼容的错误消息字段。 |
| data | object | 可选；存在时必须为对象，使用其作为凭证；不存在时兼容顶层直接返回凭证。 |
| data.accessKeyId / accessKeyId | string | 凭证必填；OSS 临时 AccessKey ID，只供内存使用，不展示、不保存原值。 |
| data.accessKeySecret / accessKeySecret | string | 凭证必填；OSS 临时密钥，只供内存使用，不展示、不保存原值。 |
| data.securityToken / securityToken | string | 凭证必填；OSS STS Token，只供内存使用，不展示、不保存原值。 |
| data.endpoint / endpoint | string | 凭证必填；OSS endpoint，可带协议。 |
| data.bucketName / bucketName | string | 凭证必填；OSS bucket 名称。 |
| data.dir / dir | string | 可选；上传对象前缀，缺省 `tmp`。 |
| data.supportedTypes / supportedTypes | string | 可选；逗号分隔扩展名列表，按服务端返回限制上传。 |
| data.maxFileSize / maxFileSize | integer / string | 可选；字节限制，数字字符串转换规则见上表。 |
| data.maxFileCount / maxFileCount | integer / string | 可选；批次次数限制，数字字符串转换规则见上表。 |
| data.ErrorCode / ErrorCode | 不限定，按响应值处理 | 出现即作为 OSS 凭证业务错误，不继续上传。 |
| data.ErrorMessage / ErrorMessage | string | 可选；配合 ErrorCode 解释凭证错误。 |

#### 凭证脚本的持久化结果

| 字段 / 输出 | 类型 | 说明 |
|---|---|---|
| 响应各字段 | 同响应 | 保留完整结构；三个密钥字段递归替换为 `[已隐藏]`，原始密钥只供 upload_files.py 内存使用。 |
| transportHttpStatus | integer / null | 记录公共 transport 的实际外层 HTTP 状态；连接未响应时为 null，不能用响应体伪装 HTTP 成功。 |
| Saved full response | string | 公共调用器保存脱敏响应并报告绝对路径；上传器内部获取凭证时捕获输出，不与上传结果混合。 |

#### OSS 上传器本地输出（非 LinkFox 接口）

| 字段 | 类型 | 说明 |
|---|---|---|
| 根节点 | array[object] | 与输入路径同序，保留部分成功与失败项。 |
| 成功项.url | string | 公开 HTTPS URL，供下游传入 imageUrls。 |
| 成功项.path | string | OSS object key。 |
| 成功项.name | string | 原始文件名。 |
| 成功项.size | integer | 文件字节数。 |
| 成功项.ext | string | 小写扩展名，无扩展名用 bin。 |
| 成功项.localPath | string | 原文件绝对路径。 |
| 失败项.error | boolean | true。 |
| 失败项.input | string | 输入路径。 |
| 失败项.message | string | 对应错误原因。 |
| stdout 附加行 | string | 成功项按原样输出 `Saved full response: <url> (<size> bytes)` 与 `Uploaded <localPath> -> <url>`。 |
| 退出码 | integer | 全部成功为 0；没有输入或任一项失败为 1。部分成功不丢弃成功结果。 |

成功 URL 登记到当前会话 `_meta.json` 的 `deliverables`，源文件名（不含扩展名）登记到 `skills_called`，并更新 `last_used_at`。会话根按以下顺序选择可写目录：ACPX_WORKSPACES 首个路径、cwd、家目录、临时目录，首次生成会话元数据和 index.jsonl。品牌结果的落盘脚本另见 [品牌基因约定](brand-gene.md#产物与-cli)。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关响应正常后，兼容 data 包装与顶层直接凭证；data 非对象、出现 ErrorCode、五个必填凭证字段缺失均停止上传。不得打印原始凭证来诊断。
- 文件失败时保留已上传成功项并非零退出；品牌提取流程遇到任一上传失败须停止，不能把本地路径或失败项传入 textgen。后续若处理失败项，不重复上传已成功项。

### curl 示例

仅在已有授权的诊断场景使用；响应包含临时密钥，不回显或记录原值，常规流程推荐脱敏业务脚本。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/getStsVoucherByAPI" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{}' | python -c 'import json,sys; d=json.load(sys.stdin); s={"accessKeyId","accessKeySecret","securityToken"}; f=lambda x: {k:("[已隐藏]" if k in s else f(v)) for k,v in x.items()} if isinstance(x,dict) else [f(v) for v in x] if isinstance(x,list) else x; print(json.dumps(f(d),ensure_ascii=False))'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-imagegen-brand-gene-extract",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
