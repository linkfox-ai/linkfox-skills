# AIGC 素材准备

本技能内置流程：本地图片或视频、外部 HTTP(S) 素材 → `scripts/upload_file.py` → Base64 上传 → 返回的公开素材地址 → 视频创建。

1. 所有素材先准备再创建；外部地址先下载再上传。不要把源 URL、本地路径、Base64 或 data URI 直接用于低层生成入口。
2. 每个不同文件或源 URL 上传一次，保留来源映射；相同来源用于多个字段时复用，多图顺序不变。只处理本次实际需要的素材，不上传无关图片或文件。
3. 核对响应和公开素材地址，失败停止；素材全部准备好后只创建一次。查询时仅用已保存任务编号，不重新上传或创建。
4. 上传免费 （限时）、同步完成，不创建异步任务、不轮询；不使用 STS、OSS 或额外依赖技能。格式、大小、图片尺寸、辅助入口参数与认证配置集中见 [接口定义](api.md#接口base64-素材上传)。

本地素材示例：

```bash
python <skill-root>/scripts/upload_file.py '{"filePath":"/absolute/path/product.png"}' --inline
```

外部素材示例：

```bash
python <skill-root>/scripts/upload_file.py '{"url":"https://source.example/product.png"}' --inline
```

辅助脚本仅在进程内持有编码，通过业务封装调用公共 runner 完成上传、鉴权和响应落盘；操作系统命令行仅含路径或 URL，不含编码或凭证。生成字段仅使用上传返回地址，完整入口自动完成转换。公开访问沿用用户本次任务授权，不重复确认。
