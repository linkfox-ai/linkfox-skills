# Lazada 评价接口

## 公共规则

请求头、网关基础地址、请求字段、响应 envelope、响应码和写入恢复统一见 [接口总览](api.md#公共规则)。本页各操作只补充业务差异。CLI 参数映射与本地输出见 [script-usage.md](script-usage.md)。

## 接口：评价历史（listReviewHistory）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /review/seller/history/list`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listReviewHistory`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `item_id` | 正整数或数字字符串 | 是 | 实际商品 ID。 |
| `start_time` | 整数或数字字符串 | 是 | 起始 Unix 毫秒时间戳，按平台规则限最近 90 天。 |
| `end_time` | 整数或数字字符串 | 是 | 结束 Unix 毫秒时间戳，时间范围最多 7 天。 |
| `current` | 整数或数字字符串 | 是 | 页码，1–50。 |
| `order_id` | 正整数或数字字符串 | 否 | 按同一店铺的订单缩小范围。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data.id_list` | 数组 | 评价 ID 列表，供 getReviews 使用。空数组表示无匹配评价。 |
| 上游 `data.current`、`page_size`、`total` | 整数或数字字符串 | 当前页、页容量、总评价数。 |
| 上游 `success`、`error_code`、`error_msg` | 布尔值或布尔字符串、字符串、字符串 | 查询标志与诊断。success=true 且 data 仅含有效 current、page_size 时，后端按已确认的空页补 id_list=[]，保留分页值且不补造 total；其他缺失结构不能仅凭 success=true 当作空结果。 |

[官方评价历史参数与响应](https://open.lazada.com/apps/doc/api?path=%2Freview%2Fseller%2Fhistory%2Flist)。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：按评价 ID 查询（getReviews）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /review/seller/list/v2`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getReviews`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id_list` | 正整数或数字字符串的数组 | 是 | 1–10 个来自评价历史的真实 ID，保留精度。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data.review_list` | 对象数组 | 评价详情列表。按实际返回的评价内容与回复字段展示。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：提交卖家回复（replyReview）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /review/seller/reply/add`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=replyReview`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 是 | 实际评价 ID。 |
| `content` | 字符串 | 是 | 用户确认的回复，最多 500 字符。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `success` 或 `data` | 布尔值或字符串 | true 表示平台确认回复成功。 |
| `status` | 字符串 | LinkFox 写入状态。 |

上游 GET 会发布卖家回复。提交前确认评价和实际回复内容。

处理评价时只展示当前任务需要的内容。反馈使用脱敏摘要。 [Lazada Open Platform](https://open.lazada.com/apps/doc/getting_started)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。
