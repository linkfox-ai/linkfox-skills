# EchoTik TikTok Influencer Profiles and Trends API 参考

## 调用规范

- 请求：`POST ${LINKFOX_TOOL_GATEWAY}/echotik/<端点>`，JSON Body。缺省网关为 `https://tool-gateway.linkfox.com`。
- 认证：Header `Authorization: <api_key>`，Key 优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`。
- 请求头：`Content-Type: application/json`、`User-Agent: LinkFox-Skill/2.0`，透传环境变量 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。
- Python 3.9+，入口脚本只依赖标准库，HTTP超时150秒。
- 请求头配置不得含CR/LF，且须能由HTTP客户端编码；非法Key或透传头在缓存、落盘和网络请求前退出1，仅指出字段名，不回显值。
- 每次成功查询预计消耗5算力，实际费用以 `X-Cost-Token`、`X-Cost-Credit` 为准，脚本将其回填为 `costToken`、`costCredit`。空结果和失败不返回正常计费成本；每次只查询一页或一个最多10人的批次。
- 日期为 `yyyy-MM-dd`，ID均为字符串。缺失字段可能省略或返回null，均表示未知，不补零。

## 批量达人详情

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/echotik/influencer/detail`
- 脚本：`scripts/echotik_influencer_detail.py`
- 上游：`GET /api/v3/echotik/influencer/detail`
- 官方文档：https://opendocs.echotik.live/echotik/influencer/detail.md

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `userIds` | array<string> | 否 | - | 两组列表必须二选一；最多10个，去重后以英文逗号传给上游。userIds为数字ID；uniqueIds为账号，不带@或URL。 |
| `uniqueIds` | array<string> | 否 | - | 两组列表必须二选一；最多10个，去重后以英文逗号传给上游。userIds为数字ID；uniqueIds为账号，不带@或URL。 |

`userIds` 每项须为1到100位数字字符串；`uniqueIds` 每项为1到100位字母、数字、句点或下划线。去除首尾空白后校验，不能传 `@账号` 或URL。单次输入条数在去重前不得超过10。

### data 对象字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `avatar` | string | avatar |
| `avg30dPrice` | number | avg_30d_price |
| `category` | string | category |
| `contactEmail` | string | contact_email |
| `ecScore` | number | ec_score |
| `firstCrawlDt` | integer (64-bit) | first_crawl_dt |
| `gender` | string | gender |
| `influencerVideoDurationLevel` | string | influencer_video_duration_level |
| `influencerVideoPublishHour` | string | influencer_video_publish_hour |
| `influencerVideoPublishWeek` | string | influencer_video_publish_week |
| `interactionRate` | number | interaction_rate |
| `language` | string | language |
| `mostCategoryProduct` | string | most_category_product |
| `mostViewsVideo` | string | most_views_video |
| `nickName` | string | nick_name |
| `offMark` | integer (64-bit) | off_mark |
| `perVideoProductViewsAvg7dCnt` | integer (64-bit) | per_video_product_views_avg_7d_cnt |
| `region` | string | region |
| `salesFlag` | integer (64-bit) | sales_flag |
| `sellerId` | string | seller_id |
| `showCaseFlag` | integer (64-bit) | show_case_flag |
| `signature` | string | signature |
| `totalCommentsCnt` | integer (64-bit) | total_comments_cnt |
| `totalDigg1dCnt` | integer (64-bit) | total_digg_1d_cnt |
| `totalDigg30dCnt` | integer (64-bit) | total_digg_30d_cnt |
| `totalDigg7dCnt` | integer (64-bit) | total_digg_7d_cnt |
| `totalDigg90dCnt` | integer (64-bit) | total_digg_90d_cnt |
| `totalDiggCnt` | integer (64-bit) | total_digg_cnt |
| `totalFollowers1dCnt` | integer (64-bit) | total_followers_1d_cnt |
| `totalFollowers30dCnt` | integer (64-bit) | total_followers_30d_cnt |
| `totalFollowers7dCnt` | integer (64-bit) | total_followers_7d_cnt |
| `totalFollowers90dCnt` | integer (64-bit) | total_followers_90d_cnt |
| `totalFollowersCnt` | integer (64-bit) | total_followers_cnt |
| `totalFollowingCnt` | integer (64-bit) | total_following_cnt |
| `totalLikesCnt` | integer (64-bit) | total_likes_cnt |
| `totalLiveCnt` | integer (64-bit) | total_live_cnt |
| `totalPostVideoCnt` | integer (64-bit) | total_post_video_cnt |
| `totalProduct30dCnt` | integer (64-bit) | total_product_30d_cnt |
| `totalProductCnt` | integer (64-bit) | total_product_cnt |
| `totalSaleCnt` | integer (64-bit) | total_sale_cnt |
| `totalSaleGmv30dAmt` | number | total_sale_gmv_30d_amt |
| `totalSaleGmvAmt` | number | total_sale_gmv_amt |
| `totalSharesCnt` | integer (64-bit) | total_shares_cnt |
| `totalVideoProduct30dCnt` | integer (64-bit) | total_video_product_30d_cnt |
| `totalVideoSale30dCnt` | integer (64-bit) | total_video_sale_30d_cnt |
| `totalViewsCnt` | integer (64-bit) | total_views_cnt |
| `uniqueId` | string | unique_id |
| `userId` | string | user_id |

## 达人历史趋势

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/echotik/influencer/trend`
- 脚本：`scripts/echotik_influencer_trend.py`
- 上游：`GET /api/v3/echotik/influencer/trend`
- 官方文档：https://opendocs.echotik.live/echotik/influencer/trend.md

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `userId` | string | 是 | - | 达人ID |
| `startDate` | string | 是 | - | 筛选时间范围，yyyy-MM-dd格式 |
| `endDate` | string | 是 | - | 筛选时间范围，yyyy-MM-dd格式 |
| `pageNum` | integer | 否 | 1 | 本服务范围1到100000 |
| `pageSize` | integer | 否 | 10 | 本服务范围1到10；一次只查询一页 |

`userId` 须为1到100位数字字符串。仅支持最近180天历史，开始日期不得早于服务端当天减180天，结束日期不得晚于当天，且开始日期不得晚于结束日期；必须为有效日历日期，不自动翻页。分页默认值用于字段省略；显式null不使用默认值。

### data 对象字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `dt` | string | 日期 |
| `totalCommentsCnt` | integer (64-bit) | 总评论量 |
| `totalDigg1dCnt` | integer (64-bit) | 近1天点赞增量 |
| `totalDiggCnt` | integer (64-bit) | 总点赞量 |
| `totalFollowers1dCnt` | integer (64-bit) | 近1天粉丝增量 |
| `totalFollowersCnt` | integer (64-bit) | 总粉丝量 |
| `totalLiveCnt` | integer (64-bit) | 总直播场次 |
| `totalPostVideoCnt` | integer (64-bit) | 总发布视频数 |
| `totalSale1dCnt` | integer (64-bit) | 近1天销量（预估） |
| `totalSaleGmv1dAmt` | number | 近1天GMV（预估） |
| `totalSharesCnt` | integer (64-bit) | 总分享量 |
| `totalViewsCnt` | integer (64-bit) | 总播放量 |
| `userId` | string | 达人ID |

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

结构示例：`{"errcode":200,"data":[{"userId":"6787875411281134598","uniqueId":"jeffreestar"}],"total":1,"requestId":"example","costToken":9000,"costCredit":5}`。示例仅展示形状，非完整生产响应；实际记录字段以上述各端点定义为准。

公开网关使用camelCase请求/记录字段；达人批量查询接收数组，由后端转为供应商GET的逗号分隔 `user_ids` 或 `unique_ids`。不要直接传逗号字符串或供应商 `code=0` 包络。记录中缺失或null的字段均按未知处理；金额字段保留原数值，未明确币种或金额单位时不自行换算。

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
curl --request POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/echotik/influencer/detail" \
  --max-time 150 \
  --header "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  --header "Content-Type: application/json" \
  --header "User-Agent: LinkFox-Skill/2.0" \
  --header "SESSION_ID: ${SESSION_ID:-}" \
  --header "MESSAGE_ID: ${MESSAGE_ID:-}" \
  --header "MODE_ID: ${MODE_ID:-}" \
  --header "APP_NAME: ${APP_NAME:-}" \
  --data '{"uniqueIds":["jeffreestar"]}'
```

curl示例直接发送请求，不应用脚本的缓存、落盘和摘要；日常任务优先使用入口脚本。

## Feedback API

可识别技能说明与实际行为不一致、结果不符合用户意图、用户评价或改进建议；仅在用户明确要求或授权反馈时，向 `POST https://skill-api.linkfox.com/api/v1/public/feedback` 发送脱敏JSON，`Content-Type: application/json`。

```json
{"skillName":"linkfox-echotik-influencer","sentiment":"NEUTRAL","category":"SUGGESTION","content":"说明已授权反馈的问题、预期行为与实际结果，不附凭证或无关会话。"}
```

`sentiment`：`POSITIVE`、`NEUTRAL`、`NEGATIVE`；`category`：`BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER`。不要发送API Key、供应商凭证、达人联系方式或无关会话内容。
