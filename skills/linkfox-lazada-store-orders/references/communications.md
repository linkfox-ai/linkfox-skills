# Lazada 评价与店铺会话接口

## 公共规则

使用 LinkFox `POST /lazada/orders` 和 `scripts/orders_api.py`，按操作提供 `connectionId`、`operation` 及对象 `params`。请求头、网关配置、写入 UUID 及状态恢复见 [履约与售后公共规则](order-operations.md#公共规则)。

### 结果路径

CLI 保存文件顶层 `data` 是业务结果。只有业务 `data` 时，后端会移除上游这一层。上游还有 `success`、`err_code` 等独立字段时保留原层次。因此下表所示“上游 `data.message_id`”对应文件中的 `data.message_id` 或 `data.data.message_id`。单独返回的上游标志位在业务 `data` 内读取。

## 评价历史（`listReviewHistory`）

上游 `GET /review/seller/history/list`。只读。

### 请求参数

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `item_id` | 正整数或数字字符串 | 是 | 实际商品 ID。 |
| `start_time` | 整数或数字字符串 | 是 | 起始 Unix 毫秒时间戳，按平台规则限最近 90 天。 |
| `end_time` | 整数或数字字符串 | 是 | 结束 Unix 毫秒时间戳，时间范围最多 7 天。 |
| `current` | 整数或数字字符串 | 是 | 页码，1–50。 |
| `order_id` | 正整数或数字字符串 | 否 | 按同一店铺的订单缩小范围。 |

### 响应字段

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data.id_list` | 数组 | 评价 ID 列表，供 getReviews 使用。空数组表示无匹配评价。 |

## 按评价 ID 查询（`getReviews`）

上游 `GET /review/seller/list/v2`。只读。

### 请求参数

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id_list` | 正整数或数字字符串的数组 | 是 | 1–10 个来自评价历史的真实 ID，保留精度。 |

### 响应字段

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data.review_list` | 对象数组 | 评价详情列表。按实际返回的评价内容与回复字段展示。 |

## 提交卖家回复（`replyReview`）

上游 `GET /review/seller/reply/add`。写入。

### 请求参数

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 是 | 实际评价 ID。 |
| `content` | 字符串 | 是 | 用户确认的回复，最多 500 字符。 |

### 响应字段

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `success` 或 `data` | 布尔值或字符串 | true 表示平台确认回复成功。 |
| `status` | 字符串 | LinkFox 写入状态。 |

上游 GET 会发布卖家回复。提交前确认评价和实际回复内容。

## 会话列表（`listChatSessions`）

上游 `GET /im/session/list`。只读。

### 请求参数

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_time` | 整数或数字字符串 | 是 | 开始时间的 Unix 毫秒时间戳。 |
| `page_size` | 整数或数字字符串 | 是 | 单页数量，至少 1。 |
| `last_session_id` | 字符串 | 否 | 用于下一页的会话游标。 |

### 响应字段

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data.session_list` | 对象数组 | 会话列表。继续分页时使用上游提供的游标。 |

## 会话详情（`getChatSession`）

上游 `GET /im/session/get`。只读。

### 请求参数

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `session_id` | 字符串 | 是 | 同一店铺的真实会话 ID。 |

### 响应字段

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data.session_id` | 字符串 | 会话 ID。 |
| 上游 `data` | 对象 | 会话详情，按实际返回字段展示。 |

## 会话消息（`listChatMessages`）

上游 `GET /im/message/list`。只读。

### 请求参数

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `session_id` | 字符串 | 是 | 同一店铺的真实会话 ID。 |
| `start_time` | 整数或数字字符串 | 是 | 开始时间的 Unix 毫秒时间戳。 |
| `page_size` | 整数或数字字符串 | 是 | 单页数量，至少 1。 |
| `last_message_id` | 字符串 | 否 | 同一会话下一页的消息游标。 |

### 响应字段

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data.message_list` | 对象数组 | 当前会话消息。继续分页时使用实际返回的游标。 |

## 发送买家消息（`sendChatMessage`）

上游 `POST /im/message/send`。写入。

### 请求参数

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `session_id` | 字符串 | 是 | 同一店铺的真实会话 ID。 |
| `template_id` | 字符串 | 是 | 1、3、4、6、10006、10007、10008 或 10010。 |
| `txt` | 字符串 | 模板 1 时 | 用户确认的文本。 |
| `img_url` | 字符串 | 模板 3 时 | 确认发送的图片地址。 |
| `video_id` | 正整数或数字字符串 | 模板 6 时 | 确认发送的视频 ID。 |
| `width`、`height` | 整数或数字字符串 | 模板 3 或 6 时 | 素材宽高，均为正整数。 |
| `item_id` | 正整数或数字字符串 | 模板 10006 时 | 商品 ID。 |
| `order_id` | 正整数或数字字符串 | 模板 10007 时 | 订单 ID。 |
| `promotion_id` | 正整数或数字字符串 | 模板 10008 时 | 促销 ID。 |

### 响应字段

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data.message_id` | 字符串 | 发送成功时返回的实际消息 ID。 |
| 上游 `success` | 布尔值或字符串 | 若为 true，可作为成功信号。 |
| 上游 `err_code` | 整数或字符串 | 0 可作为 IM 成功信号，其他已返回值表示失败。 |
| `status` | 字符串 | LinkFox 写入状态。 |

模板 `4` 和 `10010` 分别为表情及关注。发送前确认会话、内容、素材和模板。

## 标记会话已读（`markChatRead`）

上游 `POST /im/session/read`。写入。

### 请求参数

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `session_id` | 字符串 | 是 | 同一店铺的真实会话 ID。 |
| `last_read_message_id` | 字符串 | 是 | 本次标为已读的最后一条真实消息 ID。 |

### 响应字段

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `success` | 布尔值或字符串 | 若为 true，可作为成功信号。 |
| 上游 `err_code` | 整数或字符串 | 0 可作为 IM 成功信号，其他已返回值表示失败。 |
| `status` | 字符串 | LinkFox 写入状态。 |

此操作会改变会话的已读状态。

## 创建订单会话（`openChatSession`）

上游 `POST /im/session/open`。写入。

### 请求参数

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `order_id` | 正整数或数字字符串 | 是 | 当前店铺近 30 天的实际订单 ID。 |

### 响应字段

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.session_id` | 字符串 | 已建立的会话 ID。 |
| `status` | 字符串 | LinkFox 写入状态。 |

用户需要继续发送消息时，使用该会话 ID，并确认消息内容。

## 撤回消息（`recallChatMessage`）

上游 `POST /im/message/recall`。写入。

### 请求参数

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `session_id` | 字符串 | 是 | 同一店铺的真实会话 ID。 |
| `message_id` | 字符串 | 是 | 准备撤回的真实消息 ID。 |

### 响应字段

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `success` | 布尔值或字符串 | 若为 true，可作为成功信号。 |
| 上游 `err_code` | 整数或字符串 | 0 可作为 IM 成功信号，其他已返回值表示失败。 |
| `status` | 字符串 | LinkFox 写入状态。 |

Lazada 的撤回窗口为发送后 2 分钟。

处理评价和消息时只展示当前任务需要的内容。反馈使用脱敏摘要。 [Lazada Open Platform](https://open.lazada.com/apps/doc/getting_started)
