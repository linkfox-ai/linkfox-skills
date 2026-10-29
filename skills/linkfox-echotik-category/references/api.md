# EchoTik TikTok Category Intelligence API 参考

## 调用规范

- 请求：`POST ${LINKFOX_TOOL_GATEWAY}/echotik/<端点>`，JSON Body。缺省网关为 `https://tool-gateway.linkfox.com`。
- 认证：Header `Authorization: <api_key>`，Key 优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`。
- 请求头：`Content-Type: application/json`、`User-Agent: LinkFox-Skill/2.0`，透传环境变量 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。
- Python 3.9+，入口脚本只依赖标准库，HTTP超时150秒。
- 请求头配置不得含CR/LF，且须能由HTTP客户端编码；非法Key或透传头在缓存、落盘和网络请求前退出1，仅指出字段名，不回显值。
- 每次成功查询预计消耗5算力，实际费用以 `X-Cost-Token`、`X-Cost-Credit` 为准，脚本将其回填为 `costToken`、`costCredit`。空结果和失败不返回正常计费成本；每次只查询一个端点的一页。
- 日期为 `yyyy-MM-dd`，ID均为字符串。缺失字段可能省略或返回null，均表示未知，不补零。
- 类目ID和父类目ID须为1到100位数字字符串；`region` 须为两位大写区域代码，如 `US`，不自动将小写转为大写。

## 一级商品类目

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/echotik/category/l1`
- 脚本：`scripts/echotik_category_l1.py`
- 上游：`GET /api/v3/echotik/category/l1`
- 官方文档：https://opendocs.echotik.live/echotik/category/l1.md

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `language` | string | 是 | - | 具体的语言，可选：th-TH、en-US、id-ID、zh-CN、ms-MY、vi-VN其中之一 |

### data 对象字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `categoryId` | string | 分类ID |
| `categoryLevel` | string | 分类级别，1，2，3 |
| `categoryName` | string | 分类名称 |
| `language` | string | 语言 |
| `parentId` | string | 父分类ID |

## 二级商品类目

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/echotik/category/l2`
- 脚本：`scripts/echotik_category_l2.py`
- 上游：`GET /api/v3/echotik/category/l2`
- 官方文档：https://opendocs.echotik.live/echotik/category/l2.md

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `language` | string | 是 | - | 具体的语言，可选：th-TH、en-US、id-ID、zh-CN、ms-MY、vi-VN其中之一 |
| `parentId` | string | 否 | - | 父节点ID：一级分类ID |

`parentId` 按官方 OpenAPI 的可选标记处理；省略或为null时不增加父类目筛选。提供时须为对应上一级类目的数字字符串，空字符串无效。

### data 对象字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `categoryId` | string | 分类ID |
| `categoryLevel` | string | 分类级别，1，2，3 |
| `categoryName` | string | 分类名称 |
| `language` | string | 语言 |
| `parentId` | string | 父分类ID |

## 三级商品类目

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/echotik/category/l3`
- 脚本：`scripts/echotik_category_l3.py`
- 上游：`GET /api/v3/echotik/category/l3`
- 官方文档：https://opendocs.echotik.live/echotik/category/l3.md

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `language` | string | 是 | - | 具体的语言，可选：th-TH、en-US、id-ID、zh-CN、ms-MY、vi-VN其中之一 |
| `parentId` | string | 否 | - | 父节点ID：二级分类ID |

`parentId` 按官方 OpenAPI 的可选标记处理；省略或为null时不增加父类目筛选。提供时须为对应上一级类目的数字字符串，空字符串无效。

### data 对象字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `categoryId` | string | 分类ID |
| `categoryLevel` | string | 分类级别，1，2，3 |
| `categoryName` | string | 分类名称 |
| `language` | string | 语言 |
| `parentId` | string | 父分类ID |

## 一级类目大盘详情

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/echotik/category/detail`
- 脚本：`scripts/echotik_category_detail.py`
- 上游：`GET /api/v3/echotik/category/product/detail`
- 官方文档：https://opendocs.echotik.live/echotik/category/product/detail.md

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `categoryId` | string | 是 | - | 商品一级分类ID |
| `region` | string | 是 | - | 两位大写区域代码，如US |

仅支持一级商品类目ID；数据T+1更新。

### data 对象字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `categoryId` | string | 一级分类ID |
| `categoryPriceTrend` | string | 类目价格趋势 |
| `categoryTrend` | string | 类目趋势 |
| `priorityRegion` | string | 地区 |
| `totalGmv1dAmt` | number | 近1日GMV |
| `totalGmv30dAmt` | number | 近30日GMV |
| `totalGmv7dAmt` | number | 近7日GMV |
| `totalGmvAmt` | number | 总GMV |
| `totalIfl1dCnt` | integer (64-bit) | 近1日新增达人数 |
| `totalIfl30dCnt` | integer (64-bit) | 近30日新增达人数 |
| `totalIfl7dCnt` | integer (64-bit) | 近7日新增达人数 |
| `totalIflCnt` | integer (64-bit) | 总达人数 |
| `totalLiveSale1dCnt` | integer (64-bit) | 近1日直播销量 |
| `totalLiveSale30dCnt` | integer (64-bit) | 近30日直播销量 |
| `totalLiveSale7dCnt` | integer (64-bit) | 近7日直播销量 |
| `totalLiveSaleCnt` | integer (64-bit) | 总直播销量 |
| `totalProduct1dCnt` | integer (64-bit) | 近1日新增商品数 |
| `totalProduct30dCnt` | integer (64-bit) | 近30日新增商品数 |
| `totalProduct7dCnt` | integer (64-bit) | 近7日新增商品数 |
| `totalProductCnt` | integer (64-bit) | 总商品数 |
| `totalSale1dCnt` | integer (64-bit) | 近1日新增销量 |
| `totalSale30dCnt` | integer (64-bit) | 近30日新增销量 |
| `totalSale7dCnt` | integer (64-bit) | 近7日新增销量 |
| `totalSaleCnt` | integer (64-bit) | 总销量 |
| `totalSpuAvgPrice1dCnt` | number | 近1日商品均价 |
| `totalSpuAvgPrice30dCnt` | number | 近30日商品均价 |
| `totalSpuAvgPrice7dCnt` | number | 近7日商品均价 |
| `totalSpuAvgPriceCnt` | number | 当前商品均价 |

## 类目历史趋势

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/echotik/category/trend`
- 脚本：`scripts/echotik_category_trend.py`
- 上游：`GET /api/v3/echotik/category/trend`
- 官方文档：https://opendocs.echotik.live/echotik/category/trend.md

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `categoryId` | string | 否 | - | categoryId |
| `categoryL2Id` | string | 否 | - | categoryL2Id |
| `categoryL3Id` | string | 否 | - | categoryL3Id |
| `region` | string | 是 | - | 两位大写区域代码，如US |
| `startDate` | string | 是 | - | yyyy-MM-dd格式，时间范围筛选 |
| `endDate` | string | 是 | - | yyyy-MM-dd格式，时间范围筛选 |
| `pageNum` | integer | 否 | 1 | 本服务范围1到100000 |
| `pageSize` | integer | 否 | 10 | 本服务范围1到10；一次只查询一页 |

开始日期不得晚于结束日期，必须是有效日历日期；类目趋势没有套用达人趋势的最近180天限制。可选类目ID省略或为null时不增加对应筛选，空字符串无效。分页默认值用于字段省略；显式null不使用默认值。

### data 对象字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `categoryId` | string | category_id |
| `categoryL2Id` | string | category_l2_id |
| `categoryL3Id` | string | category_l3_id |
| `dt` | string | dt |
| `priorityRegion` | string | priority_region |
| `totalSale1dCnt` | integer (64-bit) | 近1日销量 |
| `totalSaleGmv1dAmt` | number | 近1日销售额 |

## 公共响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 网关成功为200；必须结合响应体判断 |
| errmsg | string | 网关安全提示 |
| data | array<object> | 当前请求返回的记录列表 |
| total | integer | 本次记录数，不是全量匹配数 |
| requestId | string/null | 上游请求ID |
| costToken | integer / decimal string | 实际计费Token，由 `X-Cost-Token` 回填；小数Token保留为十进制字符串，不取整 |
| costCredit | integer | 由 `X-Cost-Credit` 回填的实际算力，最终以当前请求为准 |
| columns | array<object> | 渲染列元数据 |
| type | string | `tableListWorkbenches` |

结构示例：`{"errcode":200,"data":[{"categoryId":"600001"}],"total":1,"requestId":"example","costToken":9000,"costCredit":5}`。示例仅展示形状，非完整生产响应；实际记录字段以上述各端点定义为准。

公开网关使用camelCase请求/记录字段；后端映射为供应商GET查询的snake_case字段。不要直接把供应商GET参数或 `code=0` 包络当作公开POST接口格式。记录中缺失或null的字段均按未知处理；金额字段保留原数值，未明确币种或金额单位时不自行换算。

## 错误处理

- 参数错误：HTTP400、`errcode=400`，不调用上游。
- 空结果：HTTP200、`errcode=10006`，不返回可计费成本。
- 上游HTTP200业务拒绝：当前公开错误码30001，展示安全提示并停止。
- 上游HTTP错误、限流、超时及非法响应：由服务统一返回安全错误；结合响应体判断，不暴露上游原文、凭证或堆栈。
- 本地配置异常：标准内部异常。对外只返回安全提示。
- 成功缓存24小时，按网关、端点、Key指纹及完整参数隔离；HTTP/业务失败均不缓存。`--no-cache` 强制刷新可能再次计费。
- 缓存文件的JSON或UTF-8损坏时按未命中处理，仅执行当前已授权查询；成功数据中的 `_cache` 元数据损坏时修复标记并复用数据，不额外请求。
- 业务失败或非法UTF-8响应规范化为安全错误，保存后退出码为2，不打印堆栈、不缓存失败。参数格式、缺少Key、落盘失败退出码为1；输出统一UTF-8和LF，不回退写入其他目录。

## curl 示例

```bash
curl --request POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/echotik/category/l1" \
  --max-time 150 \
  --header "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  --header "Content-Type: application/json" \
  --header "User-Agent: LinkFox-Skill/2.0" \
  --header "SESSION_ID: ${SESSION_ID:-}" \
  --header "MESSAGE_ID: ${MESSAGE_ID:-}" \
  --header "MODE_ID: ${MODE_ID:-}" \
  --header "APP_NAME: ${APP_NAME:-}" \
  --data '{"language":"zh-CN"}'
```

curl示例直接发送请求，不应用脚本的缓存、落盘和摘要；日常任务优先使用入口脚本。

## Feedback API

可识别技能说明与实际行为不一致、结果不符合用户意图、用户评价或改进建议；仅在用户明确要求或授权反馈时，向 `POST https://skill-api.linkfox.com/api/v1/public/feedback` 发送脱敏JSON，`Content-Type: application/json`。

```json
{"skillName":"linkfox-echotik-category","sentiment":"NEUTRAL","category":"SUGGESTION","content":"说明已授权反馈的问题、预期行为与实际结果，不附凭证或无关会话。"}
```

`sentiment`：`POSITIVE`、`NEUTRAL`、`NEGATIVE`；`category`：`BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER`。不要发送API Key、供应商凭证、达人联系方式或无关会话内容。
