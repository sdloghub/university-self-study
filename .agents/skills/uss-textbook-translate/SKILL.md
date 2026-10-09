---
name: uss-textbook-translate
description: Translate a supplied English PDF textbook into professional Chinese Markdown and a readable typeset Chinese PDF, preserving equations, figures, numbering and source-page alignment. Use when the user selects textbook translation, separate from summarizing study notes.
---

# 英文 PDF 教材专业翻译

先读 uss AGENTS.md 和教材书目信息，确认用户指定的书、版次、范围与期望格式。默认范围为给出的整本教材，输出中文 Markdown 和重新排版的中文 PDF；用户指定双语/只 Markdown/只 PDF 时遵从。翻译保存到同一教材的 `翻译/中文/`，不覆盖原件、OCR 副本或笔记。用户提供的文件可按其请求转换；仅通过书目找到的版本先按课程获取流程取得可处理原件，不把缺失全文补写成译文。

## 译前准备

按 [uss-ingestion](../uss-ingestion/SKILL.md) 优先提取原生文字，无文字层按 AGENTS.md 自动 OCR。清理重复页眉页脚、断词和多栏阅读顺序，保留物理页码与印刷页码对应；图、表、公式、脚注和代码仍须视觉核对。提取存疑不能借翻译自行修补为确定结论。

读取 [术语、版式与质量规范](references/translation-quality.md)，先确定术语表、符号表和章节结构。按学科使用规范中文术语，首次出现关键术语保留英文，跨章译法保持一致。每个原文段落、公式、图表/脚注记录来源位置，译文的重排页码不能冒充原书页码。

## 分章翻译

按章/节分批翻译并保存断点与源哈希，保留定义、定理、证明的逻辑关系、成立条件、量词、否定、单位、引用和编号。公式、变量、代码与教材数据原样保留；代码注释可译但不能改变可执行代码。译者解释单独标为译注，不混入原文。完整翻译模式不得用章节摘要替代未完成译文。

图表采用原图加中文图题/图注；必要时配双语标签表或重绘可核对的简图，保留原图与来源。公式图像不可靠时转为经过核对的数学排版，无法核对的部分列入缺口，不伪称已译。独立章节可在 OCR 等待期间推进，依赖页未就绪时保留任务状态。

## 输出与验证

Markdown 采用 Obsidian 可读结构、章节导航和数学语法。PDF 使用当前可用的 PDF 技能/工具生成，确保中文字体嵌入、目录书签、页码、可搜索文字、清晰公式和图表。目标为适合中文阅读的重新排版，不承诺逐像素还原英文版；原书位置通过来源映射保留。若选择独立 LaTeX 源文件，使用 Codex 内置编辑器与编译检查；批量 PDF 可用适合项目的既有排版工具，不自动安装整套运行环境。

先做代表性章节样张核对字体、公式、长表格与图注，再沿用版式生成全书；样张用于验证，不默认停下等待批准。渲染关键页与每章代表页，修复溢出、缺字、断行、图片分辨率与孤立标题；全文结构覆盖检查和抽样语言/视觉检查分别报告。

交付中文 PDF、章节 Markdown、术语表、源页对照和翻译进度/缺口。完整翻译须章节、段落、公式、图表与脚注覆盖可核对；未完成就注明范围，不称“全书完成”。后续更新按 [uss-notes](../uss-notes/SKILL.md) 保护人工改译和旧版本。不假装调用另一模型复核；有实际第二次核对才记录其范围。
