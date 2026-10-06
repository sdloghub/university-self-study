---
name: uss-ingestion
description: Extract university PDFs, slides and handwritten images into page-traceable raw sidecars; run the uss PDF OCR workflow for textless scans and verify visual content. Use before indexing or writing study notes.
---

# 资料提取与 OCR

先读 uss AGENTS.md 和已有提取/进度记录。保留原件；从内容确认教师课件、教材、官方讲义、用户笔记、原题、学长笔记及既有整理稿的角色。

PDF 优先原生文本；重要读取失败先按 [ingestion.md](references/ingestion.md) 使用 [pdf_probe.py](scripts/pdf_probe.py) 比较解析器，区分加密、损坏、扫描页和空白页。PPTX/DOCX 使用对应文档能力。探测字数不等于完整提取。

扫描页、手写、公式、图表或截图先读 [multimodal_ocr.md](references/multimodal_ocr.md)。确认含文字但无文字层的 PDF 按 uss AGENTS.md 自动调用项目 pdf_ocr 官方 API；当前模型视觉用于转录及关键核对。用户要求不上传时改用可用的直接视觉/本地 OCR。实际能力不足则记录缺口，不假装调用 codex/pi 或未安装模型。

原始转录先保存到课程 _extracted/，再编辑正文；公式、缩进、单位、否定词和图中关系不能丢失。区分原文、视觉解释及不确定字符。采用 [证据记录](../uss-source-index/references/evidence_quality.md)，保存原件相对路径/哈希、物理页码、印刷编号、方法与核对状态；视觉补充注明实际看过的页码。OCR 运行状态不能代替已核对状态。

长 PDF 启动 OCR 后继续独立检索/大纲工作，完成后再使用依赖全文的结论。按原件哈希去重，复用任务编号和断点，不重建工作区绕过失败。保留 OCR 副本哈希与原页映射；已有文字页使用原生提取标记。

本地 OCR 输出可用 [local_ocr_sidecar.py](scripts/local_ocr_sidecar.py) 归一化。官方 API 的结果结构不同，不能直接套用该脚本；先从带文字层 PDF 提取，再写兼容 sidecar。交给 [来源索引](../uss-source-index/SKILL.md) 建库。交付说明实际提取范围、视觉核对页与存疑。
