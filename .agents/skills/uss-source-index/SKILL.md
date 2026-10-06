---
name: uss-source-index
description: Build, update and query provenance-aware indexes of extracted course sources, preserving reviewed questions and writing progress. Use for whole courses, long textbooks, source queries and resumable study workflows.
---

# 来源索引与检索

先读 uss AGENTS.md、现有索引、进度和缺口。来源需先经 [资料提取](../uss-ingestion/SKILL.md)，不要把 PDF 原件或最终笔记直接当作已核对转录。单份短文可跳过建库；整门课程、长教材或跨会话任务使用 .course_index/。

读 [retrieval.md](references/retrieval.md) 选择 reuse/update/rebuild/defer 和脚本参数。脚本命令以本 skill 目录为工作目录，输入输出使用实际路径。增量构建保留 questions.reviewed.jsonl、人工决定和 writing 进度，不重复刷新不变来源。

[证据与题目契约](references/evidence_quality.md) 是共享记录规范：来源原件路径、哈希、物理页码、版本及提取/核对状态必须可追溯。OCR 状态和笔记正确性分开。脚本只检索候选；关键论述需读取完整相关页，必要时回看原页。

用 build_source_index.py 建索引，search_index.py 搜确切词/正则，chapter_pack.py 取完整相关章节，index_status.py 读健康状态，link_candidates.py 提出真实概念链接。coverage_check.py 的词法匹配不认证 A/B/C/D 语义覆盖；交由 [测评设计](../uss-assessment/SKILL.md) 逐题核对。

更新来源哈希时保留旧依据并标记受影响引用。来源被删不自动删人工笔记。查询任务给精确出处，不重生成课程库。来源冲突/提取存疑保留双方依据，索引结构通过不代表语义正确。写作转交 [uss-notes](../uss-notes/SKILL.md)。
