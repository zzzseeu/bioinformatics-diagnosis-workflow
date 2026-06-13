# 生物信息诊断工作流 Skill 升级设计

## 背景

当前 `docx-analysis-plan-parser` skill 主要完成一件事：解析生信项目方案 `.docx`，提取项目背景、数据、模块、图表和注意事项，并输出 SOP 级中文 Markdown 分析计划。新的目标是将其升级并重命名为 `bioinformatics-diagnosis-workflow`（中文显示名：生物信息诊断工作流），面向诊断/机制类生信项目，覆盖单细胞、转录组、bulk、多组学和客户自测序数据。

升级后的 skill 仍然保持一个用户入口，但内部拆分为阶段化工作流、代码模板、报告模板、manifest 规范和质检规则。默认每个阶段完成后暂停，等待用户确认再进入下一阶段。

## 名称与定位

- skill 目录名：`bioinformatics-diagnosis-workflow`
- metadata name：`bioinformatics-diagnosis-workflow`
- 中文显示名：`生物信息诊断工作流`
- 不兼容旧名，不在描述中保留 `docx-analysis-plan-parser`
- 触发场景：解析生信方案 Word、整理分析需求、核对需求与数据/结果、生成分析计划、生成项目分析代码、安排人工分析、基于结果生成 Word 报告、执行报告质检

## 依赖

- 必须使用已安装的 `docx` skill 处理所有 `.docx` 文档。
- 方案文档解析、报告模板读取、报告生成、模板样式保留和 Word 编辑均遵循 `docx` skill 的规则。
- `.docx` 读取优先策略为：`pandoc --track-changes=all` 可用时用于富文本抽取；需要图表/关系/章节上下文时使用 OOXML 解包；现有抽取脚本继续作为领域结构化提取工具。

## 目录结构

```text
bioinformatics-diagnosis-workflow/
  SKILL.md
  agents/openai.yaml
  assets/
    报告格式模板-20250929.docx
  references/
    workflow-stages.md
    manifest-schema.md
    module-library.md
    report-template-map.md
    report-qc-rules.md
    docx-patterns.md
  scripts/
    extract_docx_outline.py
    scan_project_results.py
    build_manifest.py
    prepare_report_inputs.py
  templates/
    code/
      bulk_de_analysis.R
      single_cell_qc_seurat.R
      enrichment_clusterprofiler.R
```

第一版实现时可以先放少量代表性代码模板，后续逐步扩展模块库。

## 阶段化工作流

默认每个阶段完成后暂停并等待用户确认。

1. 解析方案文档
   - 输入：项目方案 `.docx`
   - 行为：使用 `docx` skill 和结构化抽取脚本读取方案内容
   - 输出：需求摘要、模块清单、备注/疑问、图表要求

2. 需求与数据/结果核对
   - 输入：方案解析结果、用户提供的数据目录或结果目录
   - 行为：核对方案要求和实际文件是否匹配
   - 输出：缺口清单、冲突项、需确认信息

3. 生成完整分析计划
   - 输入：需求摘要和 gap check
   - 行为：生成 SOP 级分析计划，区分自动执行、smoke test 后人工执行、纯人工执行、报告专用模块
   - 输出：分析计划 Markdown 和 manifest

4. 基于模板生成项目代码并安全执行
   - 输入：分析计划、数据目录、代码模板
   - 行为：根据实际项目渲染或改写内置模板，生成项目专属 R/Python 脚本
   - 小数据或普通 bulk/表格分析：输入齐全时可自动运行
   - 大单细胞/长耗时分析：只做临时 smoke test，验证脚本可执行后转人工全量运行
   - 输出：正式项目脚本和代码 manifest

5. 人工分析交接
   - 输入：无法自动稳定执行或需长耗时全量执行的模块
   - 行为：输出人工执行方案、运行命令、参数、结果目录要求
   - 输出：人工任务 Markdown 和 manifest

6. 整理报告输入
   - 输入：分析结果目录、manifest、项目 memory
   - 行为：扫描图表、表格、脚本和软件包，形成报告素材索引
   - 输出：报告输入 manifest 和报告素材说明

7. 基于模板生成 Word 报告
   - 输入：报告模板、方案文档内容、结果目录、报告输入 manifest
   - 行为：调用/遵循 `docx` skill，保留模板样式并填充章节
   - 输出：`report/<项目编号>_<YYYYMMDD>_report.docx`

8. 报告质检
   - 输入：生成的报告、manifest、方案文档
   - 行为：检查章节完整性、方案一致性、图片/表格存在性、软件列表和参考文献覆盖、是否误用示例图、是否虚构结论
   - 输出：`07_report_qc.md`

## 阶段产物

每个项目默认生成 `workflow/` 目录：

```text
workflow/
  PROJECT_MEMORY.md
  01_requirements.md
  01_requirements_manifest.csv
  02_gap_check.md
  02_gap_check_manifest.csv
  03_analysis_plan.md
  03_analysis_manifest.csv
  04_generated_code.md
  04_code_manifest.csv
  05_manual_tasks.md
  05_manual_manifest.csv
  06_report_inputs.md
  06_report_manifest.csv
  07_report_qc.md
```

JSON 不作为主要交付物。必要时脚本可以内部使用临时结构化对象，但用户可见输出以 Markdown 和 CSV 为准。

## Manifest 设计

核心 manifest 使用模块级视角，便于 Excel 打开筛选：

```text
stage
module_id
module_name
source_requirement
input_required
input_found
output_expected
output_found
execution_mode
code_template
generated_script
status
manual_action
report_section
notes
```

状态值：

```text
pending
ready
auto_runnable
smoke_test_passed
manual_required
completed
blocked
skipped
```

执行模式：

```text
auto
smoke_test_then_manual
manual
report_only
not_applicable
```

## 项目长期记忆

每个项目默认生成并持续更新 `workflow/PROJECT_MEMORY.md`。它不是临时日志，而是项目状态总览。

推荐结构：

```markdown
# PROJECT_MEMORY

## 项目基本信息
- 项目编号
- 项目主题
- 疾病/表型
- 物种
- 数据类型
- 当前阶段
- 最近更新时间

## 阶段状态
| 阶段 | 状态 | 关键产物 | 待确认问题 |

## 分析模块状态
| 模块 | 执行模式 | 输入状态 | 代码状态 | 结果状态 | 报告状态 |

## 关键决策
- 日期：决策内容、原因、影响范围

## 待办与阻塞
- 待客户确认
- 待人工执行
- 待补充数据
- 待报告修订

## 结果目录约定
- 输入数据目录
- 代码目录
- 结果目录
- 报告目录

## 交接摘要
- 下一步该做什么
- 哪些文件最重要
- 哪些地方不能改
```

更新规则：

- 每完成一个阶段，都更新 `PROJECT_MEMORY.md`
- 不记录临时 smoke test 日志和失败流水账
- 只记录对项目推进有追溯价值的决策、状态和交付物
- 用户手动分析完成后，只需提供结果目录，workflow 扫描后更新 memory 和 manifest

## 代码模板与执行规则

代码模板位于 `templates/code/`，作为常用分析步骤骨架。模板不是最终代码，workflow 需要根据项目实际数据、分组、物种、阈值和输出目录生成项目专属脚本。

每个模板应包含：

- 参数占位：输入路径、分组列、物种、阈值、输出目录、图形字体、导出格式
- 输入要求：表达矩阵、metadata、Seurat 对象、DEG 表等
- 输出约定：图、表、RDS/RData
- 适用条件：可自动运行、需 smoke test 后人工运行、或只能人工运行

执行规则：

- 普通表格/bulk 分析：输入齐全、规模合理时，生成脚本并自动运行
- 单细胞/大数据/长耗时模块：生成脚本；用临时小样本或测试对象做 smoke test；通过后删除测试数据和测试日志；标记为人工全量执行
- 数据库/网页/GUI 依赖分析：默认生成人工方案和结果目录要求
- 不确定模块：标记为 `blocked` 或 `manual_required`，等待用户确认
- 最终只保留正式项目代码、manifest、阶段 Markdown、PROJECT_MEMORY 和报告；不保留临时测试数据、测试日志和通过/失败记录

模板优先级：

1. 使用 skill 内置代码模板
2. 如项目已有同类脚本，优先复用项目脚本风格
3. 如模板缺失，生成模块专属脚本，并将可复用部分作为后续模板候选

## 报告模板与章节规则

报告模板作为 skill asset：

```text
assets/报告格式模板-20250929.docx
```

报告默认输出：

```text
report/<项目编号>_<YYYYMMDD>_report.docx
```

若同一天重复生成，为避免覆盖，追加版本号：

```text
report/<项目编号>_<YYYYMMDD>_report_v2.docx
```

模板章节：

```text
1 项目概述
  1.1 项目背景
  1.2 分析方法
  1.3 数据来源
  1.4 研究目标
  1.5 拟解决的关键科学问题
  1.6 创新性
  1.7 流程图
2 分析结果
3 项目总结
4 项目调整
5 软件列表
6 报告质检
参考文献
```

内容来源规则：

- 分析结果前的章节内容从方案文档复制/规范化，不能根据结果随意改写核心背景、目标、数据来源和流程
- 第六章节“报告质检”从方案文档复制；若方案文档无对应内容，则按模板/质检规则生成固定质检表并标注来源
- `2 分析结果` 结合项目实际分析结果输出，不照搬方案示例图
- `3 项目总结` 基于实际完成结果、关键发现、模型/机制线索和验证情况总结，不虚构不存在的结论
- `4 项目调整` 记录实际执行中相对方案的调整，如缺数据、模块改手动、阈值调整、无显著结果处理
- `5 软件列表` 从实际生成/运行脚本和 manifest 汇总软件、R 包、Python 包和数据库
- `参考文献` 从方案文档 PMID/参考文献、实际使用软件/数据库引用、分析模块引用中汇总，不凭空添加

## Word 插图规则

- Word 正文中只插 PNG 图片
- PDF 图件不插入 Word，只作为交付附件或结果文件保留
- 每张图的顺序固定为：图片、图片名称、图注
- 图片、图片名称、图注全部居中显示
- 图片名称使用加粗字体，颜色为浅蓝色
- 图注默认不加粗，只居中显示
- 如果同一结果只有 PDF 没有 PNG，报告阶段标记缺 PNG，需要补导出，不自动用 PDF 代替

## 报告质检规则

- 章节是否齐全
- 方案要求的模块是否在分析结果或项目调整中有交代
- 图表文件是否存在
- Word 中插入的图片是否均为 PNG
- 图、图名、图注顺序和居中样式是否正确
- 图名是否加粗且为浅蓝色
- 软件列表是否覆盖实际脚本使用的软件/包
- 参考文献是否覆盖方案和实际分析工具
- 是否存在示例图被误当真实结果
- 是否存在虚构基因、数据集、样本量、结论
- 报告中的项目编号、疾病、物种、数据来源是否与方案一致

## 错误处理

- 方案文档解析失败：优先用 `docx` skill 的 pandoc/OOXML fallback；仍失败则停止并说明缺失内容
- 需求和数据不匹配：不硬改方案，生成 gap check 和需确认清单
- 输入数据缺失：对应模块标记 `blocked` 或 `manual_required`
- 自动代码运行失败：修复脚本后可重试；临时测试数据和测试日志最终删除，不写入项目交付目录
- 大数据模块：只做 smoke test，正式全量运行交给用户手动执行
- 报告结果缺图/缺表：报告中不编造结果，写入项目调整/待补充，并在质检中标出
- 模板编辑失败：保留中间 Markdown 报告素材，停止修改 Word，避免产出损坏文档

## 实施范围

第一期目标：

- 重命名 skill
- 增加模板资产
- 更新 `SKILL.md`、agents metadata、references 和 manifest 规范
- 保留并增强现有 DOCX 解析脚本
- 增加结果目录扫描、manifest 生成、项目 memory 规则
- 报告生成先做到根据模板和素材生成结构化报告草稿
- 加入少量代表性代码模板，验证模板化生成项目代码的模式

第二期目标：

- 扩展常用 R/Python 模板库
- 为每个模板补充输入/输出规范
- 完善 smoke test 规则
- 逐步覆盖单细胞、bulk、机器学习、富集、PPI、GSEA、报告图表等模块

## 测试与验证

- DOCX 解析脚本保留现有单元测试，并增加方案章节、报告模板章节和 OOXML fallback 场景
- manifest 生成脚本用小型 fixture 验证字段完整性和状态值
- 代码模板用最小示例数据做 smoke test，不把临时测试数据或日志保留到项目目录
- 报告生成用模板副本验证章节填充、报告命名、PNG 插图顺序与样式
- 质检规则用缺图、缺软件列表、示例图误用等 fixture 验证

## 非目标

- 第一版不承诺覆盖所有生信分析模块
- 不把大规模单细胞全量分析默认自动跑完
- 不保留临时 smoke test 数据、日志或通过/失败记录
- 不生成 JSON 作为主要用户交付物
- 不兼容旧 skill 名称
