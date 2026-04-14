---
name: jupyter-notebook
description: 在用户请求为实验、探索或教程创建、搭建或编辑 Jupyter 笔记本（`.ipynb`）时使用；优先使用捆绑的模板并运行辅助脚本 `new_notebook.py`
  来生成一个干净的起始笔记本。
---
# Jupyter Notebook 技能

为两种主要模式创建简洁、可重现的 Jupyter 笔记本：

- 实验与探索性分析
- 教程与面向教学的分步演示

优先使用捆绑的模板和辅助脚本，以获得一致的结构并减少 JSON 错误。

## 何时使用
- 从头创建一个新的 `.ipynb` 笔记本。
- 将粗略的笔记或脚本转换为结构化的笔记本。
- 重构现有笔记本，使其更可重现且更易浏览。
- 构建将被他人阅读或重新运行的实验或教程。

## 决策树
- 如果请求是探索性的、分析性的或基于假设的，请选择 `experiment`。
- 如果请求是教学性的、逐步的或针对特定受众的，请选择 `tutorial`。
- 如果编辑现有笔记本，请将其视为重构：保留原意并改进结构。

## 技能路径

Skill files are located under `.claude/skills/jupyter-notebook/` in the project root.

## 工作流程
1. 确定意图。
Identify the notebook kind: `experiment` or `tutorial`.
Capture the objective, audience, and what "done" looks like.

2. 从模板搭建脚手架。
Use the helper script to avoid hand-authoring raw notebook JSON.

```bash
python .claude/skills/jupyter-notebook/scripts/new_notebook.py \
  --kind experiment \
  --title "Compare prompt variants" \
  --out scripts/python/
```

```bash
python .claude/skills/jupyter-notebook/scripts/new_notebook.py \
  --kind tutorial \
  --title "Intro to embeddings" \
  --out scripts/python/
```

3. 用小的、可运行的步骤填充笔记本。
Keep each code cell focused on one step.
Add short markdown cells that explain the purpose and expected result.
Avoid large, noisy outputs when a short summary works.

4. 应用合适的模式。
For experiments, follow `references/experiment-patterns.md`.
For tutorials, follow `references/tutorial-patterns.md`.

5. 在处理现有笔记本时安全编辑。
Preserve the notebook structure; avoid reordering cells unless it improves the top-to-bottom story.
Prefer targeted edits over full rewrites.
If you must edit raw JSON, review `references/notebook-structure.md` first.

6. 验证结果。
Run the notebook top-to-bottom when the environment allows.
If execution is not possible, say so explicitly and call out how to validate locally.
Use the final pass checklist in `references/quality-checklist.md`.

## 模板与辅助脚本
- 模板位于 `assets/experiment-template.ipynb` 和 `assets/tutorial-template.ipynb`。
- 辅助脚本位于 `scripts/new_notebook.py`，用于加载模板、更新标题并生成笔记本。

## 临时与输出约定
- 对于中间文件使用 `tmp/jupyter-notebook/`；完成后删除。
- 在此仓库中工作时，将最终产物写入 `scripts/python/`。
- 使用稳定且描述性的文件名（例如，`ablation-temperature.ipynb`）。

## 依赖项（仅在需要时安装）
Prefer `uv` for dependency management.

Optional Python packages for local notebook execution:

```bash
uv pip install jupyterlab ipykernel
```

The bundled scaffold script uses only the Python standard library and does not require extra dependencies.

## 环境
No required environment variables.

## Notebook 自包含原则

**禁止外部导入**: 本项目的 notebook 环境不支持从 `.py` 文件导入模块。所有代码必须内联在 notebook 中。

### 规范要求
- ❌ **禁止**: `from scripts.python.module import function`
- ❌ **禁止**: `from . import helper`
- ✅ **允许**: 标准库和第三方包 (`import pandas`, `import matplotlib.pyplot as plt`)
- ✅ **允许**: 在 notebook 内部定义辅助函数

### 原因
- Notebook 运行在特定环境中，Python 模块路径不可用
- 确保可移植性：notebook 可以在任何有相同依赖的环境中运行
- 避免隐式依赖：所有代码都可见，便于审查和调试

### 实现建议
- 将复用函数定义在 notebook 的第一个代码单元格中
- 使用类或辅助函数组织代码，而不是外部模块
- 依赖项仅限标准包：`pandas`, `numpy`, `matplotlib`, `seaborn`, `sklearn` 等

## 参考映射
- `references/experiment-patterns.md`: 实验结构与启发式准则。
- `references/tutorial-patterns.md`: 教程结构与教学流程。
- `references/notebook-structure.md`: 笔记本 JSON 结构与安全编辑规则。
- `references/quality-checklist.md`: 最终验证检查清单。

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
免责声明：
本文件已使用 AI 翻译服务 [Co-op Translator](https://github.com/Azure/co-op-translator) 进行翻译。虽然我们努力保证准确性，但自动翻译可能存在错误或不准确之处。应以原文（原始语言版本）为准。对于重要信息，建议采用专业人工翻译。由于使用本翻译而导致的任何误解或误释，我们概不负责。
<!-- CO-OP TRANSLATOR DISCLAIMER END -->
---

## Gotchas

<!-- Document frequently encountered issues and their solutions -->

### Configuration
| Issue | Solution |
|-------|----------|
| | |

### Data/Input
| Issue | Solution |
|-------|----------|
| | |

### Processing
| Issue | Solution |
|-------|----------|
| | |

### Output/Export
| Issue | Solution |
|-------|----------|
| | |

### Environment
| Issue | Solution |
|-------|----------|
| | |
