# 图片与环境准备

## 选择可用的 Python

本次任务选择一个真实可用的命令并始终复用，记为 `<PYTHON>`。Windows 按 `py -3`、`python`、`python3` 顺序尝试；其他系统按 `python3`、`python` 顺序尝试。

每个候选必须执行以下命令，退出码为 0 且标准输出包含非空解释器路径才算可用。WindowsApps 的空输出占位命令不得选用。

```text
<候选命令> -c "import sys; print(sys.executable)"
```

## 检查 Pillow 的 WebP 能力

当前环境首次调用本技能前，使用选定解释器执行：

```text
<PYTHON> -c "from PIL import features; ok=features.check('webp'); print('WEBP_OK' if ok else 'WEBP_MISSING'); raise SystemExit(0 if ok else 1)"
```

只有退出码为 0 且标准输出包含 `WEBP_OK` 才算通过。失败时静默安装一次：

```text
<PYTHON> -m pip install --disable-pip-version-check "Pillow>=10.4,<13"
```

随后用同一解释器重新检查一次。再次失败时停止并报告依赖初始化失败，不进入收费图搜，不循环安装，不要求用户手工转换图片。后续调用检查通过即可执行，不重复安装。

## 本地图片上传

用户提供本地路径时先执行：

```text
<PYTHON> scripts/upload_image.py "/path/to/local/image.png"
```

标准输出为 `{"url":"<公开图片链接>"}`，用该链接作为后续图搜图片来源。文件格式映射、上传约定和链接有效期见 [接口定义](api.md)。图片链接、Base64 和图片标识的条件、转换优先级也统一见接口定义。

预处理始终由业务脚本负责：JPEG/PNG 原样传递；WebP 读取首帧、纠正 EXIF 方向，透明区域铺白后以 quality=90 转 JPEG。URL 来源转换后临时写入 JPEG 再上传，临时转换文件用后清理；完整接口响应仍保存于当前工作目录，不写临时目录。
