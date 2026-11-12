# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件说明本地 CLI 输入、构参和保存结果；CLI 补充字段不是网关 DTO。业务字段以各接口参考为准。

## 共享脚本约定

### 脚本输入与构参

使用 Python 3.9+，普通业务入口和公共调用器仅用标准库。具名脚本接受一个 JSON 对象；带操作名的入口接受 `<操作> '<JSON 参数>'` 或 `<操作> --params-file <UTF-8 JSON 文件>`，两种参数来源互斥。各操作名大小写固定，无额外别名。

| 参数／选项 | 类型 | 默认／说明 |
|---|---|---|
| `connectionId` | 字符串 | 从当前用户店铺列表原样取值，不复用其他用户连接。 |
| `params` | 对象 | 业务操作默认 `{}`，有必填业务参数时仍须提供；原生对象／数组不转换为字符串，明确要求 JSON／XML 文本的字段除外。 |
| `requestId` | 字符串 | 写入或续查须提供带连字符 UUID，脚本转成小写；不自动生成，不用于只读业务查询。 |
| `--params-file` | CLI 选项 | 仅带操作名的入口支持，读取 UTF-8／UTF-8 BOM JSON；不上传参数文件本身。 |
| `--inline` | CLI 开关 | 默认关闭，开启时打印全部可保存数据，同时仍保存文件。 |
| `--no-cache` | CLI 开关 | 所有业务调用均实时执行，无缓存读写；保留此兼容选项，不允许重试或跳过保存。 |

网关与双 Key 的优先级、请求头及超时见 [公共规则](api.md#公共规则)。未知顶层字段会在请求前拒绝；业务层只构参、检查业务结果，公共 `call_api.run` 统一传输和保存。ID 保持原类型和精度，不把字符串 ID 转成浮点数。

### 脚本输出与业务结果

输出先经过预检，再发起一次请求，不自动重试。结果保存到当前工作目录 `linkfox/<YYYY-MM-DD>/<session>/data/`，优先使用 `SESSION_ID`，缺省使用时间和随机标识；文件名包含技能、操作、时间及随机后缀。输出或元数据不可写时在请求前失败，不回退到临时目录。

| 本地字段 | 类型 | 说明 |
|---|---|---|
| `data` | 对象、数组或操作允许的标量／null | 去除可选网关外层包装后的业务结果，保留内层层次和类型；凭据与不应展示的敏感字段被移除。 |
| `requestId` | 字符串或 null | 上游请求标识。 |
| `clientRequestId` | 字符串 | 写入／续查使用的原 UUID，异常时仍尽可能保留。 |
| `status` | 字符串 | 原写记录或授权申请状态，不与 HTTP 状态混用。 |
| `success` | 布尔值 | CLI 调用结果。写入仅 `SUCCEEDED` 为 true；成功查询状态时仍须检查原 `status`。 |
| `httpStatus`、`errcode`、`errorCode`、`code` | 整数或字符串，可缺省 | 失败时可保留的网关传输诊断；不等于上游 HTTP。 |
| `error` | 字符串，可缺省 | 本地错误分类。 |
| `traceId`、`upstreamCode`、`upstreamRequestId` | 字符串，可缺省 | 经过格式校验的跟踪标识或从服务端安全消息提取的上游诊断。 |

响应不超过 8000 字节时打印完整脱敏 JSON；较大响应打印顶层字段、诊断和最大列表的长度及最多前三项样本。以 `Saved full response:` 后的实际路径为准。`--inline` 不解除脱敏。业务失败、HTTP／网关／结构异常为非零退出；本地参数／输出预检失败通常为 2，远程失败为 1，成功为 0。原始错误正文、Key 和店铺令牌不保存。

`REAUTHORIZATION_REQUIRED` 先核对店铺授权，`LAZADA_PROXY_FORBIDDEN` 核对代理出口；`SellerNotVerified` 表示卖家未验证；范围和权限问题不当作 LinkFox 登录或计费故障。写入结果不明时仅用原 UUID 查询状态，核对目标实际状态后再决定下一步。

## 接口：listVouchers

### 脚本输入与构参

`python scripts/marketing_api.py listVouchers '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口listvouchers)；不展开为顶层字段。 |

脚本固定填入 `operation=listVouchers`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /promotion/vouchers/get`。参数约束与业务字段见 [接口说明](api.md#接口listvouchers)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口listvouchers) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：getVoucher

### 脚本输入与构参

`python scripts/marketing_api.py getVoucher '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口getvoucher)；不展开为顶层字段。 |

脚本固定填入 `operation=getVoucher`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /promotion/voucher/get`。参数约束与业务字段见 [接口说明](api.md#接口getvoucher)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口getvoucher) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：createVoucher

### 脚本输入与构参

`python scripts/marketing_api.py createVoucher '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口createvoucher)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=createVoucher`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/voucher/create`。参数约束与业务字段见 [接口说明](api.md#接口createvoucher)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口createvoucher) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：updateVoucher

### 脚本输入与构参

`python scripts/marketing_api.py updateVoucher '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口updatevoucher)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=updateVoucher`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/voucher/update`。参数约束与业务字段见 [接口说明](api.md#接口updatevoucher)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口updatevoucher) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：activateVoucher

### 脚本输入与构参

`python scripts/marketing_api.py activateVoucher '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口activatevoucher)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=activateVoucher`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/voucher/activate`。参数约束与业务字段见 [接口说明](api.md#接口activatevoucher)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口activatevoucher) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：deactivateVoucher

### 脚本输入与构参

`python scripts/marketing_api.py deactivateVoucher '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口deactivatevoucher)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=deactivateVoucher`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/voucher/deactivate`。参数约束与业务字段见 [接口说明](api.md#接口deactivatevoucher)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口deactivatevoucher) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：listVoucherProducts

### 脚本输入与构参

`python scripts/marketing_api.py listVoucherProducts '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口listvoucherproducts)；不展开为顶层字段。 |

脚本固定填入 `operation=listVoucherProducts`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /promotion/voucher/products/get`。参数约束与业务字段见 [接口说明](api.md#接口listvoucherproducts)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口listvoucherproducts) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：addVoucherSkus

### 脚本输入与构参

`python scripts/marketing_api.py addVoucherSkus '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口addvoucherskus)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=addVoucherSkus`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/voucher/product/sku/add`。参数约束与业务字段见 [接口说明](api.md#接口addvoucherskus)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口addvoucherskus) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：removeVoucherSkus

### 脚本输入与构参

`python scripts/marketing_api.py removeVoucherSkus '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口removevoucherskus)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=removeVoucherSkus`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/voucher/product/sku/remove`。参数约束与业务字段见 [接口说明](api.md#接口removevoucherskus)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口removevoucherskus) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：listFreeShipping

### 脚本输入与构参

`python scripts/marketing_api.py listFreeShipping '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口listfreeshipping)；不展开为顶层字段。 |

脚本固定填入 `operation=listFreeShipping`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /promotion/freeshippings/get`。参数约束与业务字段见 [接口说明](api.md#接口listfreeshipping)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口listfreeshipping) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：getFreeShipping

### 脚本输入与构参

`python scripts/marketing_api.py getFreeShipping '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口getfreeshipping)；不展开为顶层字段。 |

脚本固定填入 `operation=getFreeShipping`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /promotion/freeshipping/get`。参数约束与业务字段见 [接口说明](api.md#接口getfreeshipping)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口getfreeshipping) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：createFreeShipping

### 脚本输入与构参

`python scripts/marketing_api.py createFreeShipping '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口createfreeshipping)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=createFreeShipping`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/freeshipping/create`。参数约束与业务字段见 [接口说明](api.md#接口createfreeshipping)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口createfreeshipping) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：updateFreeShipping

### 脚本输入与构参

`python scripts/marketing_api.py updateFreeShipping '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口updatefreeshipping)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=updateFreeShipping`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/freeshipping/update`。参数约束与业务字段见 [接口说明](api.md#接口updatefreeshipping)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口updatefreeshipping) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：activateFreeShipping

### 脚本输入与构参

`python scripts/marketing_api.py activateFreeShipping '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口activatefreeshipping)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=activateFreeShipping`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/freeshipping/activate`。参数约束与业务字段见 [接口说明](api.md#接口activatefreeshipping)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口activatefreeshipping) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：deactivateFreeShipping

### 脚本输入与构参

`python scripts/marketing_api.py deactivateFreeShipping '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口deactivatefreeshipping)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=deactivateFreeShipping`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/freeshipping/deactivate`。参数约束与业务字段见 [接口说明](api.md#接口deactivatefreeshipping)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口deactivatefreeshipping) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：listFreeShippingProducts

### 脚本输入与构参

`python scripts/marketing_api.py listFreeShippingProducts '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口listfreeshippingproducts)；不展开为顶层字段。 |

脚本固定填入 `operation=listFreeShippingProducts`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /promotion/freeshipping/products/get`。参数约束与业务字段见 [接口说明](api.md#接口listfreeshippingproducts)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口listfreeshippingproducts) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：addFreeShippingSkus

### 脚本输入与构参

`python scripts/marketing_api.py addFreeShippingSkus '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口addfreeshippingskus)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=addFreeShippingSkus`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/freeshipping/product/sku/add`。参数约束与业务字段见 [接口说明](api.md#接口addfreeshippingskus)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口addfreeshippingskus) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：removeFreeShippingSkus

### 脚本输入与构参

`python scripts/marketing_api.py removeFreeShippingSkus '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口removefreeshippingskus)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=removeFreeShippingSkus`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/freeshipping/product/sku/remove`。参数约束与业务字段见 [接口说明](api.md#接口removefreeshippingskus)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口removefreeshippingskus) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：listFreeShippingRegions

### 脚本输入与构参

`python scripts/marketing_api.py listFreeShippingRegions '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口listfreeshippingregions)；不展开为顶层字段。 |

脚本固定填入 `operation=listFreeShippingRegions`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /promotion/freeshipping/regions/get`。参数约束与业务字段见 [接口说明](api.md#接口listfreeshippingregions)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口listfreeshippingregions) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：listShippingOptions

### 脚本输入与构参

`python scripts/marketing_api.py listShippingOptions '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口listshippingoptions)；不展开为顶层字段。 |

脚本固定填入 `operation=listShippingOptions`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /promotion/freeshipping/deliveryoptions/get`。参数约束与业务字段见 [接口说明](api.md#接口listshippingoptions)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口listshippingoptions) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：listFlexiCombo

### 脚本输入与构参

`python scripts/marketing_api.py listFlexiCombo '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口listflexicombo)；不展开为顶层字段。 |

脚本固定填入 `operation=listFlexiCombo`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /promotion/flexicombo/list`。参数约束与业务字段见 [接口说明](api.md#接口listflexicombo)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口listflexicombo) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：getFlexiCombo

### 脚本输入与构参

`python scripts/marketing_api.py getFlexiCombo '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口getflexicombo)；不展开为顶层字段。 |

脚本固定填入 `operation=getFlexiCombo`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /promotion/flexicombo/details`。参数约束与业务字段见 [接口说明](api.md#接口getflexicombo)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口getflexicombo) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：createFlexiCombo

### 脚本输入与构参

`python scripts/marketing_api.py createFlexiCombo '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口createflexicombo)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=createFlexiCombo`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/flexicombo/create`。参数约束与业务字段见 [接口说明](api.md#接口createflexicombo)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口createflexicombo) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：updateFlexiCombo

### 脚本输入与构参

`python scripts/marketing_api.py updateFlexiCombo '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口updateflexicombo)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=updateFlexiCombo`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/flexicombo/update`。参数约束与业务字段见 [接口说明](api.md#接口updateflexicombo)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口updateflexicombo) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：activateFlexiCombo

### 脚本输入与构参

`python scripts/marketing_api.py activateFlexiCombo '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口activateflexicombo)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=activateFlexiCombo`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/flexicombo/activate`。参数约束与业务字段见 [接口说明](api.md#接口activateflexicombo)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口activateflexicombo) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：deactivateFlexiCombo

### 脚本输入与构参

`python scripts/marketing_api.py deactivateFlexiCombo '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口deactivateflexicombo)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=deactivateFlexiCombo`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/flexicombo/deactivate`。参数约束与业务字段见 [接口说明](api.md#接口deactivateflexicombo)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口deactivateflexicombo) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：listFlexiComboProducts

### 脚本输入与构参

`python scripts/marketing_api.py listFlexiComboProducts '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口listflexicomboproducts)；不展开为顶层字段。 |

脚本固定填入 `operation=listFlexiComboProducts`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /promotion/flexicombo/products/list`。参数约束与业务字段见 [接口说明](api.md#接口listflexicomboproducts)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口listflexicomboproducts) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：addFlexiComboSkus

### 脚本输入与构参

`python scripts/marketing_api.py addFlexiComboSkus '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口addflexicomboskus)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=addFlexiComboSkus`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/flexicombo/products/add`。参数约束与业务字段见 [接口说明](api.md#接口addflexicomboskus)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口addflexicomboskus) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：removeFlexiComboSkus

### 脚本输入与构参

`python scripts/marketing_api.py removeFlexiComboSkus '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口removeflexicomboskus)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=removeFlexiComboSkus`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /promotion/flexicombo/products/delete`。参数约束与业务字段见 [接口说明](api.md#接口removeflexicomboskus)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口removeflexicomboskus) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：listSponsoredMaxCampaigns

### 脚本输入与构参

`python scripts/marketing_api.py listSponsoredMaxCampaigns '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口listsponsoredmaxcampaigns)；不展开为顶层字段。 |

脚本固定填入 `operation=listSponsoredMaxCampaigns`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /sponsor/solution/smax/searchSmaxCampaign`。参数约束与业务字段见 [接口说明](api.md#接口listsponsoredmaxcampaigns)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口listsponsoredmaxcampaigns) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：getSponsoredMaxOverview

### 脚本输入与构参

`python scripts/marketing_api.py getSponsoredMaxOverview '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口getsponsoredmaxoverview)；不展开为顶层字段。 |

脚本固定填入 `operation=getSponsoredMaxOverview`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /sponsor/solution/smax/report/getReportOverview`。参数约束与业务字段见 [接口说明](api.md#接口getsponsoredmaxoverview)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口getsponsoredmaxoverview) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：getSponsoredMaxMetric

### 脚本输入与构参

`python scripts/marketing_api.py getSponsoredMaxMetric '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口getsponsoredmaxmetric)；不展开为顶层字段。 |

脚本固定填入 `operation=getSponsoredMaxMetric`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `GET /sponsor/solution/smax/report/getReportOverviewMetric`。参数约束与业务字段见 [接口说明](api.md#接口getsponsoredmaxmetric)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口getsponsoredmaxmetric) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：createSponsoredMaxCampaign

### 脚本输入与构参

`python scripts/marketing_api.py createSponsoredMaxCampaign '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口createsponsoredmaxcampaign)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=createSponsoredMaxCampaign`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /sponsor/solution/smax/addSMaxAASolution`。参数约束与业务字段见 [接口说明](api.md#接口createsponsoredmaxcampaign)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口createsponsoredmaxcampaign) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：updateSponsoredMaxCampaign

### 脚本输入与构参

`python scripts/marketing_api.py updateSponsoredMaxCampaign '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口updatesponsoredmaxcampaign)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=updateSponsoredMaxCampaign`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /sponsor/solution/smax/updateSmaxCampaign`。参数约束与业务字段见 [接口说明](api.md#接口updatesponsoredmaxcampaign)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口updatesponsoredmaxcampaign) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：setSponsoredMaxCampaignStatus

### 脚本输入与构参

`python scripts/marketing_api.py setSponsoredMaxCampaignStatus '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口setsponsoredmaxcampaignstatus)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=setSponsoredMaxCampaignStatus`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/marketing` → `POST /sponsor/solution/smax/updateSmaxStatusWithoutAd`。参数约束与业务字段见 [接口说明](api.md#接口setsponsoredmaxcampaignstatus)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口setsponsoredmaxcampaignstatus) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：查询写入状态（operationStatus）

### 脚本输入与构参

`python scripts/marketing_api.py operationStatus '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `requestId` | UUID 字符串 | 是，原写入 UUID 转小写发送；不传 `operation` 和 `params`。 |


网关及上游映射为 `POST /lazada/operationStatus`。参数约束与业务字段见 [接口说明](api.md#接口查询写入状态operationstatus)。

### 脚本输出与业务结果

保存原 `clientRequestId`、上游 `requestId`、`status`、`data` 和 `success`。状态查询完成即可 `success=true`；原写入仍可能 `REJECTED`、`PARTIAL` 或 `UNKNOWN`。
