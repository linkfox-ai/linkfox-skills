# Partner EU — Promotion 接口目录

Partner Platform for EU 菜单：**Promotion / 电商促销**（与 US 版对齐的 **6** 个 `bg.promotion.*` `type`）。

文档根 `menu_code`（浏览器地址栏常见）：`7289390cfd724be4a196f11ebe45a896`。

本 skill 经 `temu_eu_proxy`（`POST /temu/proxy`）调用，默认 **`site=eu`**、**`tokenPurpose=product-inventory`**。

> EU Partner 各子菜单 `sub_menu_code` 请在 [partner-eu.temu.com](https://partner-eu.temu.com/documentation) 按 `type` 打开后补全。

## 已接入（6）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| — | `bg.promotion.activity.query` | `eu_promotion_activity_query.py` | [apis/bg-promotion-activity-query.md](./apis/bg-promotion-activity-query.md) |
| — | `bg.promotion.activity.candidate.goods.query` | `eu_promotion_activity_candidate_goods_query.py` | [apis/bg-promotion-activity-candidate-goods-query.md](./apis/bg-promotion-activity-candidate-goods-query.md) |
| — | `bg.promotion.activity.goods.query` | `eu_promotion_activity_goods_query.py` | [apis/bg-promotion-activity-goods-query.md](./apis/bg-promotion-activity-goods-query.md) |
| — | `bg.promotion.activity.goods.enroll` | `eu_promotion_activity_goods_enroll.py` | [apis/bg-promotion-activity-goods-enroll.md](./apis/bg-promotion-activity-goods-enroll.md) |
| — | `bg.promotion.activity.goods.operation.query` | `eu_promotion_activity_goods_operation_query.py` | [apis/bg-promotion-activity-goods-operation-query.md](./apis/bg-promotion-activity-goods-operation-query.md) |
| — | `bg.promotion.activity.goods.update` | `eu_promotion_activity_goods_update.py` | [apis/bg-promotion-activity-goods-update.md](./apis/bg-promotion-activity-goods-update.md) |

## 官方文档 URL

| type | URL |
|------|-----|
| `bg.promotion.activity.query` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.promotion.activity.candidate.goods.query` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.promotion.activity.goods.query` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.promotion.activity.goods.enroll` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.promotion.activity.goods.operation.query` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.promotion.activity.goods.update` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |

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
| **促销/营销活动**（本 skill） | **`linkfox-temu-promotion-eu`** |
| 商品管理 | `linkfox-temu-manage-product-eu` |
| 价格 | `linkfox-temu-price-eu` |
| 广告 Ads | `linkfox-temu-ads-eu` |
| 美国站促销 | `linkfox-temu-promotion-us` |
| 全球站促销 | `linkfox-temu-promotion-global` |

## Token 说明

建议使用 **`tokenPurpose=product-inventory`**。详见 [access-token.md](./access-token.md)。


## 接入新操作的维护约定

仅在取得 Partner 的 type、sub_menu_code、URL 及完整 Request/Response 参数表后扩展：新增 `references/apis/<type-slug>.md`，新增调用 `_eu_promotion_script.run_cli` 的 `scripts/eu_promotion_<slug>.py`，同步本目录、`references/apis/README.md` 和 SKILL.md 接口清单。不根据菜单名推测活动创建或优惠券接口。
