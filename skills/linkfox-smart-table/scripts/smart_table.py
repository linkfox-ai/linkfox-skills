#!/usr/bin/env python3
"""智能表格（LinkFox 在线多维表格）- LinkFox Skill 统一入口。

用法：
  python smart_table.py <op> '<JSON 参数>' [--inline] [--yes]

<op> 用接口名（与 /smartTable/<op> 一致），也接受旧 skill 后缀的写法（如 create-records）：

  表      listMyTables  listSharedTables  createTable  addTable  copyNotebook
  删除    deleteNotebook  deleteTable  deleteNotebookItem（一律进回收站；还原只能在页面上）
  改名    renameNotebook  renameTable  renameNotebookItem（只改名字；列名改不了）
  表头    listFields  addFields  deleteFields
  记录    listRecords  createRecords  updateRecords  deleteRecords
  附件    uploadAttachment
  AI 出图 fillAiField  getAiFillStatus
  工作流  listWorkflows（只读；关联的登记 / 换表 / 解除由工作流侧保存时自动同步，这里不提供）

--inline  强制把完整响应打印到 stdout（默认 > 8KB 只打摘要；完整响应始终落盘）
--yes     只有删除类操作认它（deleteFields / deleteRecords / deleteNotebook / deleteTable /
          deleteNotebookItem）：确认执行删除；缺它一律拒绝执行（退出码 2）

每个 op 的实现在同目录 op_<snake>.py（本地预检、确认闸门、摘要都在那里），本文件只做分派：
把 sys.argv 改成 [op, ...其余参数] 后调对应模块的 main()，退出码原样透传。
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# op（接口名）→ 模块文件名后缀（也是旧 skill 的后缀，kebab 写法）
OPS = {
    "listMyTables": "list-my-tables",
    "listSharedTables": "list-shared-tables",
    "createTable": "create-table",
    "addTable": "add-table",
    "copyNotebook": "copy-notebook",
    "deleteNotebook": "delete-notebook",
    "deleteTable": "delete-table",
    "deleteNotebookItem": "delete-notebook-item",
    "renameNotebook": "rename-notebook",
    "renameTable": "rename-table",
    "renameNotebookItem": "rename-notebook-item",
    "listFields": "list-fields",
    "addFields": "add-fields",
    "deleteFields": "delete-fields",
    "listRecords": "list-records",
    "createRecords": "create-records",
    "updateRecords": "update-records",
    "deleteRecords": "delete-records",
    "uploadAttachment": "upload-attachment",
    "fillAiField": "fill-ai-field",
    "getAiFillStatus": "get-ai-fill-status",
    "listWorkflows": "list-workflows",
}
_BY_KEBAB = {kebab: op for op, kebab in OPS.items()}


def _usage_and_exit():
    print(__doc__.strip(), file=sys.stderr)
    sys.exit(1)


def _resolve(name):
    if name in OPS:
        return name
    if name in _BY_KEBAB:
        return _BY_KEBAB[name]
    # 大小写写歪（listrecords / ListRecords）也认，只要能唯一对上
    lowered = {op.lower(): op for op in OPS}
    return lowered.get(name.lower())


def _load(op):
    snake = OPS[op].replace("-", "_")
    path = os.path.join(HERE, f"op_{snake}.py")
    # 模块里 `from linkfox_paths import ...` 要能在同目录找到
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    spec = importlib.util.spec_from_file_location(f"smart_table_op_{snake}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        _usage_and_exit()

    op = _resolve(args[0])
    if op is None:
        print(f"未知操作：{args[0]!r}。可用的操作：{', '.join(OPS)}", file=sys.stderr)
        sys.exit(1)

    module = _load(op)
    sys.argv = [f"smart_table.py {op}"] + args[1:]
    module.main()


if __name__ == "__main__":
    main()
