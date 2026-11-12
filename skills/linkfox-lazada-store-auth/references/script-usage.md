# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件说明本地 CLI 输入、构参和保存结果；CLI 补充字段不是网关 DTO。业务字段以各接口参考为准。

## 共享脚本约定

### 脚本输入与构参

使用 Python 3.9+，普通业务入口和公共调用器仅用标准库。具名脚本接受一个 JSON 对象；带操作名的入口接受 `<操作> '<JSON 参数>'` 或 `<操作> --params-file <UTF-8 JSON 文件>`，两种参数来源互斥。各操作名大小写固定，无额外别名。

| 参数／选项 | 类型 | 默认／说明 |
|---|---|---|
| `connectionId` | 字符串 | 从当前用户店铺列表原样取值，不复用其他用户连接。授权申请接口的字段另见对应小节。 |
| `params` | 对象 | 业务操作默认 `{}`，有必填业务参数时仍须提供；原生对象／数组不转换为字符串，明确要求 JSON／XML 文本的字段除外。 |
| `requestId` | 字符串 | 授权申请 ID 见对应命令。 |
| `--params-file` | CLI 选项 | 仅带操作名的入口支持，读取 UTF-8／UTF-8 BOM JSON；不上传参数文件本身。 |
| `--inline` | CLI 开关 | 默认关闭，开启时打印全部可保存数据，同时仍保存文件。 |
| `--no-cache` | CLI 开关 | 所有业务调用均实时执行，无缓存读写；保留此兼容选项，不允许重试或跳过保存。 |

网关与双 Key 的优先级、请求头及超时见 [公共规则](api.md#公共规则)。未知顶层字段会在请求前拒绝；业务层只构参、检查业务结果，公共 `call_api.run` 统一传输和保存。ID 保持原类型和精度，不把字符串 ID 转成浮点数。

### 脚本输出与业务结果

输出先经过预检，再发起一次请求，不自动重试。结果保存到当前工作目录 `linkfox/<YYYY-MM-DD>/<session>/data/`，优先使用 `SESSION_ID`，缺省使用时间和随机标识；文件名包含技能、操作、时间及随机后缀。输出或元数据不可写时在请求前失败，不回退到临时目录。

| 本地字段 | 类型 | 说明 |
|---|---|---|
| `data` | 对象、数组或操作允许的标量／null | 去除可选网关外层包装后的业务结果，保留内层层次和类型；凭据与不应展示的敏感字段被移除。授权命令使用下方单独的输出结构。 |
| `requestId` | 字符串或 null | 上游请求标识；授权命令中为授权申请 ID。 |
| `status` | 字符串 | 授权申请状态，不与 HTTP 状态混用。 |
| `success` | 布尔值 | CLI 调用结果。按对应接口响应判断，授权状态查询完成不等于已绑定。 |
| `httpStatus`、`errcode`、`errorCode`、`code` | 整数或字符串，可缺省 | 失败时可保留的网关传输诊断；不等于上游 HTTP。 |
| `error` | 字符串，可缺省 | 本地错误分类。 |
| `traceId`、`upstreamCode`、`upstreamRequestId` | 字符串，可缺省 | 经过格式校验的跟踪标识或从服务端安全消息提取的上游诊断。 |

响应不超过 8000 字节时打印完整脱敏 JSON；较大响应打印顶层字段、诊断和最大列表的长度及最多前三项样本。以 `Saved full response:` 后的实际路径为准。`--inline` 不解除脱敏。业务失败、HTTP／网关／结构异常为非零退出；本地参数／输出预检失败通常为 2，远程失败为 1，成功为 0。原始错误正文、Key 和店铺令牌不保存。

`REAUTHORIZATION_REQUIRED` 先核对店铺授权，`LAZADA_PROXY_FORBIDDEN` 核对代理出口；`SellerNotVerified` 表示卖家未验证；范围和权限问题不当作 LinkFox 登录或计费故障。

## 接口：发起授权（authorizeUrl）

### 脚本输入与构参

`python scripts/authorize_url.py '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `shopName` | 字符串 | 否，省略时提交 `{}`；最大 256 字符。 |

输入对象原样发送，不增加 `operation`。

网关及上游映射为 `POST /lazada/authorizeUrl`。参数约束与业务字段见 [接口说明](api.md#接口发起授权authorizeurl)。

### 脚本输出与业务结果

输出 JSON 仅含 `requestId`、`status`、`success`；验证后的临时授权链接单独打印给当前用户，不存文件。允许的链接为 `https://auth.lazada.com/oauth/authorize`，拒绝携带令牌的链接。

## 接口：查询授权结果（authorizationStatus）

### 脚本输入与构参

`python scripts/authorization_status.py '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `requestId` | 字符串 | 是，原授权申请 ID，不变更。 |

输入对象原样发送，不增加 `operation`。

网关及上游映射为 `POST /lazada/authorizationStatus`。参数约束与业务字段见 [接口说明](api.md#接口查询授权结果authorizationstatus)。

### 脚本输出与业务结果

保存 `requestId`、`status`、`success`。查询成功可为 `PENDING`／`AUTHORIZED`／`DENIED`／`FAILED`／`EXPIRED`，不等于已完成绑定。

## 接口：已连接店铺（authorizedStores）

### 脚本输入与构参

`python scripts/authorized_stores.py '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `{}` | 对象 | 无业务字段，读取当前用户连接。 |

输入对象原样发送，不增加 `operation`。

网关及上游映射为 `POST /lazada/authorizedStores`。参数约束与业务字段见 [接口说明](api.md#接口已连接店铺authorizedstores)。

### 脚本输出与业务结果

保存 `total`、`stores`、`success`。仅保留连接 ID、站点、卖家 ID、店铺名与状态；总数缺省时用列表长度。

## 接口：解除连接（disconnect）

### 脚本输入与构参

`python scripts/disconnect.py '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，当前用户指定连接。 |

输入对象原样发送，不增加 `operation`。

网关及上游映射为 `POST /lazada/disconnect`。参数约束与业务字段见 [接口说明](api.md#接口解除连接disconnect)。

### 脚本输出与业务结果

保存 `connectionId`、`disconnected`、`success`，仅 `disconnected=true` 为成功。结果不明先重新列店。

## 接口：店铺资料（getSeller）

### 脚本输入与构参

`python scripts/store_api.py getSeller '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口店铺资料getseller)；不展开为顶层字段。 |

脚本固定填入 `operation=getSeller`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/store` → `GET /seller/get`。参数约束与业务字段见 [接口说明](api.md#接口店铺资料getseller)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口店铺资料getseller) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。 上游附带 `_trace_id_` 等独立字段时，店铺业务对象位于 `data.data`；没有该包装时位于 `data`。先按实际结构取对象，不把缺失字段当作 false／0。

## 接口：店铺指标（getSellerMetrics）

### 脚本输入与构参

`python scripts/store_api.py getSellerMetrics '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口店铺指标getsellermetrics)；不展开为顶层字段。 |

脚本固定填入 `operation=getSellerMetrics`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/store` → `GET /seller/metrics/get`。参数约束与业务字段见 [接口说明](api.md#接口店铺指标getsellermetrics)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口店铺指标getsellermetrics) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。 上游附带 `_trace_id_` 等独立字段时，店铺业务对象位于 `data.data`；没有该包装时位于 `data`。先按实际结构取对象，不把缺失字段当作 false／0。
