# Partner EU — Ads 接口目录

Partner Platform for EU 菜单：**Ads / 电商广告**（Search & Recommend 广告，`temu.searchrec.ad.*`，与 US 版对齐 **7** 个 `type`）。

文档根 `menu_code`（浏览器地址栏常见）：`7289390cfd724be4a196f11ebe45a896`。

本 skill 经 `temu_eu_proxy`（`POST /temu/proxy`）调用，默认 **`site=eu`**、**`tokenPurpose=product-inventory`**。

> EU Partner 各子菜单 `sub_menu_code` 请在 [partner-eu.temu.com](https://partner-eu.temu.com/documentation) 按 `type` 打开后补全。

## 已接入（7）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| — | `temu.searchrec.ad.roas.pred` | `eu_ads_searchrec_ad_roas_pred.py` | [apis/temu-searchrec-ad-roas-pred.md](./apis/temu-searchrec-ad-roas-pred.md) |
| — | `temu.searchrec.ad.reports.mall.query` | `eu_ads_searchrec_ad_reports_mall_query.py` | [apis/temu-searchrec-ad-reports-mall-query.md](./apis/temu-searchrec-ad-reports-mall-query.md) |
| — | `temu.searchrec.ad.create` | `eu_ads_searchrec_ad_create.py` | [apis/temu-searchrec-ad-create.md](./apis/temu-searchrec-ad-create.md) |
| — | `temu.searchrec.ad.detail.query` | `eu_ads_searchrec_ad_detail_query.py` | [apis/temu-searchrec-ad-detail-query.md](./apis/temu-searchrec-ad-detail-query.md) |
| — | `temu.searchrec.ad.log.query` | `eu_ads_searchrec_ad_log_query.py` | [apis/temu-searchrec-ad-log-query.md](./apis/temu-searchrec-ad-log-query.md) |
| — | `temu.searchrec.ad.goods.create.query` | `eu_ads_searchrec_ad_goods_create_query.py` | [apis/temu-searchrec-ad-goods-create-query.md](./apis/temu-searchrec-ad-goods-create-query.md) |
| — | `temu.searchrec.ad.modify` | `eu_ads_searchrec_ad_modify.py` | [apis/temu-searchrec-ad-modify.md](./apis/temu-searchrec-ad-modify.md) |

## 官方文档 URL

| type | URL |
|------|-----|
| `temu.searchrec.ad.roas.pred` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.searchrec.ad.reports.mall.query` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.searchrec.ad.create` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.searchrec.ad.detail.query` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.searchrec.ad.log.query` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.searchrec.ad.goods.create.query` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.searchrec.ad.modify` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |

## 上游 OpenAPI（EU）

`POST` https://openapi-b-eu.temu.com/openapi/router（经 LinkFox 网关 `site=eu` 转发）

## 通用脚本

| 脚本 | 说明 |
|------|------|
| `temu_eu_proxy.py` | 任意 `type` + `params` |
| `temu_eu_file_download.py` | 加签文件下载 |

## 相关 skill

| 能力 | skill |
|------|--------|
| **广告 Ads**（本 skill） | **`linkfox-temu-ads-eu`** |
| 促销/营销活动 | `linkfox-temu-promotion-eu` |
| 商品管理 | `linkfox-temu-manage-product-eu` |
| 价格 | `linkfox-temu-price-eu` |
| 美国站广告 | `linkfox-temu-ads-us` |
| 全球站广告 | `linkfox-temu-ads-global` |

## Token 说明

建议使用 **`tokenPurpose=product-inventory`**。详见 [access-token.md](./access-token.md)。

加签文件下载为第 8 个操作，完整定义见 [api.md](api.md#接口加签文件下载)。
