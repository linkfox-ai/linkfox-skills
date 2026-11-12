# POD 本地图片上传

本说明仅用于新增的 POD 图片检测。原侵权 TRO 四项全检继续使用原有流程和 `upload_image.py`，本页不改变原能力的输入、上传或检测规则。

已有可公开访问的 HTTP(S) 图片 URL 直接填入 `mainProductImage`，不重复上传。本地图片和附件优先使用本包的文件上传脚本，取得公开 URL 后再检测，避免 Agent 手工生成或拼接 Base64。

需要使用本包上传脚本时，先说明图片将获得公开可访问 URL，确认用户允许公开后执行。用户仅说“上传图片”不等于已确认公开；不要公开敏感或私密内容。

```bash
python scripts/upload_file.py <本地图片路径> [<更多本地图片路径> ...]
```

脚本使用已有 `POST /oss/file/presignedPut` → 带签名地址 PUT 流程，不依赖 `oss2`，不改写源图，不自动重试。仅在内存中使用上传签名，不打印或保存带签名的上传 URL。预签名 HTTP 字段见 [api.md](api.md#接口获取图片上传预签名presignedput)；POD 上传脚本的校验、输出和错误处理以本页为准。

`upload_file.py` 接受 jpg/jpeg/png/gif/webp，单张原图不超过 10 MiB；不存在、空文件、格式或大小不符合要求的项在请求前报错。多文件按输入顺序处理，单项失败保留其他项的成功结果，任一失败时脚本非零退出。只把成功项的 `url` 交给检测；不自动调用检测接口，不重复上传成功项。

stdout 是 JSON 数组。读取没有 `error=true` 的项的 `url`，不要把失败项的消息或本地路径当作 URL。完整结果保存在当前工作目录的 `linkfox/<日期>/<session>/data/linkfox-maidalv-product-tro-detection-upload-file-<timestamp>.json`，保存路径写 stderr。

| 字段 | 类型 | 出现条件与含义 |
|---|---|---|
| url | string | 上传成功时返回的公开图片 URL，不含上传签名查询参数；用于检测的 `mainProductImage`。 |
| path | string | 上传成功时返回的对象路径，不含开头的 `/`。 |
| name | string | 上传成功时返回的本地文件名。 |
| size | integer | 上传成功时返回的原始文件大小，单位为字节。 |
| ext | string | 上传成功时返回的不带点的小写扩展名。 |
| localPath | string | 上传成功时返回的本地图片绝对路径。 |
| error | boolean | 失败项为 `true`；成功项不包含此字段。 |
| input | string | 失败项对应的原始输入路径。 |
| message | string | 失败阶段及可展示的错误原因。 |
| metadataError | string | 图片已上传成功、但本地会话元数据登记失败时返回；该项仍保留 `url` 等成功字段。 |

脚本非零退出不代表每张图片都上传失败。出现 `metadataError`，或 stderr 提示结果保存失败时，先保留 stdout 中已有的成功 URL，处理本地保存或登记问题后直接复用，不重新上传成功项；不要把整个批次再次执行。尚未执行的项会以失败项返回，不会伪装为上传成功。

原 `upload_image.py <本地图片路径>` 入口及其单对象 `{"url":"公开图片URL"}` 输出保持兼容。默认流程使用新的 `upload_file.py`；POD 不接受 HEIC。

Base64/data URI 仍是接口支持的输入方式，但不作为本地图片的默认准备方式。用户明确要求该方式时，必须由程序读取原图自动编码，Agent 不打印、分段复制或手工拼接 Base64。

公开 URL 的保留时间由服务端存储策略决定，预签名的有效期不是公开对象的保留期。上传后及时使用 URL，不承诺固定 24 小时后删除。
