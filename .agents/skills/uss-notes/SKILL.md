---
name: uss-notes
description: Write and safely update source-traceable university notes, merged study guides and original teaching material while preserving human edits. Use after source extraction and when the user requests learning artifacts.
---

# 笔记写作与安全发布

先读 uss AGENTS.md、目标课程复合大纲、已核对转录与现有人工修改。单文件只做请求的笔记；整门课程生成课程入口及必要章节；查询转交 [来源索引](../uss-source-index/SKILL.md)，不重写全库。

写作前读 [证据规范](../uss-source-index/references/evidence_quality.md) 和 [knowledge_base.md](references/knowledge_base.md)。每个重要概念/连贯主题引用存在的原始文件精确物理页；保留术语，解释含义、成立条件、符号/单位和具体例子。程序例解释行为及预期结果，执行前审查代码。agent 推导、改编例子、外校补充与课程原文分开。

自编教材采用原创讲解、推导、例子和来源定位。综合大纲的南科大基线、跨校补充、个人拓展保持标记，不大段复制教材。合并笔记与详细笔记来自同一份已核对内容，合并稿必须含实际解释，不能只有目录。概念卡片只为稳定可复用概念建立；避免重复通用解释和模板自测。练习和考卷仅按用户需求交 [uss-assessment](../uss-assessment/SKILL.md)。

沿用用户路径及 Obsidian/普通 Markdown 语法；[vault_structure.md](references/vault_structure.md) 仅为可选布局，不能强制考试目录、固定自测或“小白理解”。当前软件行为有版本变化时查官方资料并区别课程历史说法。来源冲突和提取存疑显式保留。

更新/续做读 [workflow.md](references/workflow.md)，分开最终稿、_extracted/、_working/ 和 .course_index/。用 scripts/safe_publish.py 以已知基线 dry-run，再应用无冲突改动；不能把未知人工修改当作 pristine 基线。冲突候选留在 staging，保留人工改动。大规模迁移先备份。

交付前用 scripts/validate_vault.py 检查结构，小任务 --mode lightweight；回看关键论述原页、检查推导和边界条件，环境可用时运行代表性已审查代码。结构、证据和学科检查分别报告；记录真实输出、验证状态、缺口、章节/来源版本进度，不宣称所有页已视觉核对。
