---
name: uss-textbook-notes
description: Turn each supplied textbook into its own course-aligned, chapter-based Obsidian Markdown note set with precise source pages. Use for textbook study or the default uss course workflow; keep different books and editions separate.
---

# 教材到课程与章节笔记

先读 uss AGENTS.md、课程 syllabus、教学日历和已有进度。用户给出教材即进入本流程；不要求先有大学 syllabus。无 syllabus 时依据教材目录建立自主学习单元，注明“教材自学划分”，不能冒充官方课程。

## 定位与拆分

每一本教材、每一个版次单独建立 `课程/<学校>/<代码-名称>/教材/<作者-书名-版次>/`，课程身份不明确时用 `课程/自主学习/<主题>/`。保留既有课程路径，按相同子目录规则续做，不能因规范化复制整门旧课程。多本教材共用课程入口，各自保留章节笔记、来源、进度和练习定位，不覆盖主教材。

确认封面、版权页、目录、版次与完整页数，保存原件 SHA-256。资料提取使用 [uss-ingestion](../uss-ingestion/SKILL.md)，需要 OCR 时按 AGENTS.md 自动调用；来源索引用 [uss-source-index](../uss-source-index/SKILL.md)。读取实际章节，不能根据目录或检索摘要生成“已完成”正文。

先建“课程单元—教学周次—教材章/节—物理页—能力目标”映射。一册覆盖多个课程时建立具名课程单元和先修路径；不把每章机械称为独立大学课程。保留原书章号和节号，教学日历顺序与原书顺序分别列示。识别跨章依赖与选读范围，未被 syllabus 要求的内容标为教材扩展。

## Obsidian 笔记

读取 [笔记结构与章节模板](references/obsidian-notes.md)。每章形成实际可学习的 Markdown 正文，必要时按长节拆分，统一课程入口、教材入口、章节导航。用 YAML 属性、Obsidian 数学语法、callout 和明确相对链接；不依赖第三方插件才能阅读。

笔记按原书结构提炼定义、定理及条件、推导、例子、图示说明和易错点，区分教材原文、agent 解释和用户补充。公式与关键论证核对原页；若数学 OCR 存疑，先视觉检查，保留待核对项。不得因全文处理而逐段复制原书，章节笔记用原创解释和精确引用。现成题仅做题号/页码索引；PS、考卷及答案生成只在用户要求时交 [uss-assessment](../uss-assessment/SKILL.md)。

## 长书续做与交付

按章/节和源文件哈希保存状态：未读取、已提取、已起草、已核对；每次交付注明真实完成范围，续做保留人工编辑、索引审阅记录和原件。默认推进用户给出的整本范围，不以空模板充当全文完成。OCR 等待时整理已可用章节和独立资料，依赖未识别内容的笔记待其完成。

用 [uss-notes](../uss-notes/SKILL.md) 安全发布，检查章节导航、附件路径、数学显示、物理页引用和 syllabus 覆盖；代表性章节实际预览 Markdown，不能把结构校验称为全部内容已核对。交付教材入口、章节笔记、教学日历映射和缺口清单。
