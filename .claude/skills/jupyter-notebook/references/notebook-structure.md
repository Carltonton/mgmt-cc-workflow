# 笔记本结构

Jupyter 笔记本是具有以下高层结构的 JSON 文档:

- `nbformat` 和 `nbformat_minor`
- `metadata`
- `cells` (一个由 Markdown 和代码单元组成的列表)

在以编程方式编辑 `.ipynb` 文件时:

- 保持模板中的 `nbformat` 和 `nbformat_minor`.
- 将 `cells` 保持为有序列表；除非有意，否则不要重新排序.
- 对于代码单元，当未知时将 `execution_count` 设置为 `null`.
- 对于代码单元，在搭建脚手架时将 `outputs` 设置为空列表.
- 对于 Markdown 单元，保持 `cell_type="markdown"` 和 `metadata={}`.

优先从捆绑的模板或 `new_notebook.py` (例如 `.claude/skills/jupyter-notebook/scripts/new_notebook.py`) 进行脚手架搭建，而不是手工编写原始笔记本 JSON.
