# Partner Global — Ads 接口目录

Partner Platform for **Global** 菜单：**Ads / 电商广告**（Search & Recommend 广告，`temu.searchrec.ad.*`，与 US 版对齐 **7** 个 `type`）。

文档根 `menu_code`（与 `linkfox-temu-fulfillment-global` 等一致）：`7289390cfd724be4a196f11ebe45a896`。

本 skill 经 `temu_global_proxy`（`POST /temu/proxy`）调用，默认 **`site=global`**、**`tokenPurpose=product-inventory`**。

> Global Partner 各子菜单 `sub_menu_code` 请在 [partner-global.temu.com](https://partner-global.temu.com/documentation) 按 `type` 打开后补全。

## 已接入（7）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| — | `temu.searchrec.ad.roas.pred` | `global_ads_searchrec_ad_roas_pred.py` | [apis/temu-searchrec-ad-roas-pred.md](./apis/temu-searchrec-ad-roas-pred.md) |
| — | `temu.searchrec.ad.reports.mall.query` | `global_ads_searchrec_ad_reports_mall_query.py` | [apis/temu-searchrec-ad-reports-mall-query.md](./apis/temu-searchrec-ad-reports-mall-query.md) |
| — | `temu.searchrec.ad.create` | `global_ads_searchrec_ad_create.py` | [apis/temu-searchrec-ad-create.md](./apis/temu-searchrec-ad-create.md) |
| — | `temu.searchrec.ad.detail.query` | `global_ads_searchrec_ad_detail_query.py` | [apis/temu-searchrec-ad-detail-query.md](./apis/temu-searchrec-ad-detail-query.md) |
| — | `temu.searchrec.ad.log.query` | `global_ads_searchrec_ad_log_query.py` | [apis/temu-searchrec-ad-log-query.md](./apis/temu-searchrec-ad-log-query.md) |
| — | `temu.searchrec.ad.goods.create.query` | `global_ads_searchrec_ad_goods_create_query.py` | [apis/temu-searchrec-ad-goods-create-query.md](./apis/temu-searchrec-ad-goods-create-query.md) |
| — | `temu.searchrec.ad.modify` | `global_ads_searchrec_ad_modify.py` | [apis/temu-searchrec-ad-modify.md](./apis/temu-searchrec-ad-modify.md) |

## 官方文档 URL

| type | URL |
|------|-----|
| `temu.searchrec.ad.roas.pred` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.searchrec.ad.reports.mall.query` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.searchrec.ad.create` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.searchrec.ad.detail.query` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.searchrec.ad.log.query` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.searchrec.ad.goods.create.query` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.searchrec.ad.modify` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |

## 上游 OpenAPI（Global）

`POST` https://openapi-b-global.temu.com/openapi/router（经 LinkFox 网关 `site=global` 转发）

## 通用脚本

| 脚本 | 说明 |
|------|------|
| `temu_global_proxy.py` | 任意 `type` + `params` |
| `temu_global_file_download.py` | 加签文件下载 |

## 相关 skill

| 能力 | skill |
|------|--------|
| **广告 Ads**（本 skill） | **`linkfox-temu-ads-global`** |
| 促销/营销活动 | `linkfox-temu-promotion-global` |
| 商品管理 | `linkfox-temu-manage-product-global` |
| 价格 | `linkfox-temu-price-global` |
| 美国站广告 | `linkfox-temu-ads-us` |
| 欧洲站广告 | `linkfox-temu-ads-eu` |

## Token 说明

建议使用 **`tokenPurpose=product-inventory`**。详见 [access-token.md](./access-token.md)。

> **说明**：`temu.searchrec.ad.reports.goods.query` 等操作尚未接入独立文档与脚本；扩展需要包含完整请求和响应定义的 Partner 文档，`Partner Platform-rgq.htm` 当前不可用。
