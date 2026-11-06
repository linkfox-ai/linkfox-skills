# Amazon 店铺报告脚本说明

报告脚本提供端到端获取、本地依赖检测、下载解压和短时本机 HTTP 交付。授权、选店与令牌刷新由 `linkfox-amazon-store-auth` 负责。

## 业务入口

```bash
python scripts/check_auth_dependency.py --json
python scripts/get_report.py '{"sellerId":"A1EC6SZ7XAMURH","region":"NA","reportType":"GET_MERCHANT_LISTINGS_ALL_DATA","marketplaceIds":["ATVPDKIKX0DER"]}' --inline
```

参数、默认值、环境变量、输出字段及退出码统一见 [运行约定](../references/api.md#运行约定)；逐类型日期、reportOptions 和权限见 [请求索引](../references/report-requests/types/README.md)。

## 列出现有报告

getReports 可直接按 [接口说明](../references/api.md) 调用网关；端到端 CLI 用于创建与下载报告。

## 文档维护工具

`merge_report_type_values_from_cache.py` 从 `references/_spapi_docs_cache/` 中预先准备的 15 个报告分类 HTML 缓存提取说明，更新 `references/report-requests/types/`，不发起网络请求，也不是响应缓存。依赖 beautifulsoup4；可 `pip install beautifulsoup4`，或安装到 `scripts/_pydeps` 并设置 PYTHONPATH。使用前核对缓存来源；维护不属于日常报告流程。

## 交付与错误

stderr 展示进度、响应归档位置、文件信息和最多前五行预览。stdout 在保存完整最终响应后输出 JSON 或摘要；开启 HTTP 时输出后保持服务至计时结束。访问同机地址可下载已解压文件；启动服务失败时保留本地路径和 file URI。

FATAL、CANCELLED、权限不足、网关或上游异常、超时均停止；不自动换报告类型或重建任务。详细处理见 [店铺保护](../references/spapi-protection.md)。
