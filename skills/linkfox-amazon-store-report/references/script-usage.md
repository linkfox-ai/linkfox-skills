# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：列出现有报告（getReports）

### 脚本输入与构参

#### 上游方法与资源路径

- **method**：`GET`
- **path**：`reports/2021-06-30/reports`

#### 操作参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| reportTypes | string | 是（首次查询） | 报告类型列表，逗号分隔；如 GET_MERCHANT_LISTINGS_ALL_DATA。 |
| marketplaceIds | string | 否 | 目标站点 ID 列表，逗号分隔。 |
| processingStatuses | string | 否 | 状态筛选：IN_QUEUE / IN_PROGRESS / DONE / FATAL / CANCELLED，逗号分隔。 |
| pageSize | integer | 否 | 每页条数，按上游约定。 |
| createdSince | string | 否 | ISO 8601，创建时间起点。 |
| createdUntil | string | 否 | ISO 8601，创建时间终点。 |
| nextToken | string | 否 | 上一页返回的分页令牌；翻页以令牌约定为准，不自动探测。 |

此操作按网关接口说明直接调用；get_report.py CLI 用于创建与下载报告。

### 脚本输出与业务结果

## 接口：创建报告（createReport）

### 脚本输入与构参

#### 上游方法与资源路径

- **method**：`POST`
- **path**：`reports/2021-06-30/reports`

#### 操作参数

`body` 必须是 JSON 字符串，反序列化后包含以下字段；脚本同名字段逐项映射，reportOptions 对象原样写入。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| reportType | string | 是 | [完整报告类型](report-types.md)；不得擅自更换用户指定类型。 |
| marketplaceIds | array[string] | 是 | 目标 marketplace ID 列表，多数报告至少一个。 |
| dataStartTime | string | 视报告 | ISO 8601；部分 Schema 仅采用 YYYY-MM-DD 日期部分。 |
| dataEndTime | string | 视报告 | ISO 8601 或对应 Schema 要求的日期格式。 |
| lastUpdatedDate | string | 视报告 | 部分 Vendor 报告必填，与其他日期字段组合以对应报告专页为准。 |
| reportOptions | object | 视报告 | Brand Analytics、销售流量、促销/优惠券及部分 Vendor 等需要；键、必填及枚举见逐类型专页。 |

带 JSON 结果的报告见 [Schema 索引](report-requests/README.md)；所有 109 个枚举见 [逐类型请求索引](report-requests/types/README.md)。Flat File / TSV 报告无独立 JSON Schema 时仍保留最小请求、日期、权限、站点和 reportOptions 约定，不能用最小示例绕过必填项。

### 脚本输出与业务结果


#### 业务结果使用

保留实际返回的 reportId，供后续状态查询。

## 接口：查询报告状态（getReport）

### 脚本输入与构参

#### 上游方法与资源路径

- **method**：`GET`
- **path**：`reports/2021-06-30/reports/{reportId}`

#### 操作参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| reportId | string | 是 | path 中的报告任务标识，来自创建结果或选定的已有报告；按路径分段百分号编码。 |

`get_report.py` 在创建后自动用同一个 reportId 查询状态；手工流程按网关接口说明调用该任务路径，无需报告列表的筛选或分页参数。

### 脚本输出与业务结果


#### 业务结果使用

DONE 时使用实际返回的 reportDocumentId；FATAL / CANCELLED 时停止。

## 接口：获取报告文档（getReportDocument）

### 脚本输入与构参

#### 上游方法与资源路径

- **method**：`GET`
- **path**：`reports/2021-06-30/documents/{reportDocumentId}`

#### 操作参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| reportDocumentId | string | 是 | path 中的文档标识，来自 DONE 的报告；按路径分段百分号编码。 |

### 脚本输出与业务结果


#### 业务结果使用

使用本次实际返回的 url 下载并按内容解压；不补造文档字段。
