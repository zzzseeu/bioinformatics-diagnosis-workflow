# Module Library

Use these concise SOP patterns when the Word document includes matching modules. This is not a closed taxonomy; preserve new modules from the source document.

## Execution Mode Hints

- Bulk/table analyses can be `auto` when inputs are small and complete.
- Single-cell and long-running analyses default to `smoke_test_then_manual`.
- GUI, online database, or Cytoscape-heavy steps default to `manual`.
- Report-only sections use `report_only`.

## Bulk Differential Expression
目的: 筛选疾病组与对照组差异表达基因。
输入: 表达矩阵、分组信息、平台注释。
方法与工具: RNA-seq counts 使用 DESeq2/edgeR；芯片或标准化矩阵使用 limma。
关键参数: 常用阈值 `adj.P.Val < 0.05` 且 `|log2FC| > 0.5` 或按原文阈值。
输出结果: DEG 表、上调/下调基因列表。
预期图表: 火山图、热图，PNG/PDF，Times New Roman。
质控与调整策略: DEG 过少时放宽 logFC；批次明显时加入批次校正或模型协变量。

## Single-Cell QC, Clustering, Annotation
目的: 构建单细胞图谱并注释细胞类型。
输入: 10X 矩阵、Seurat 对象或 h5ad。
方法与工具: Seurat/Scanpy；必要时 DoubletFinder/Scrublet；SingleR 和文献 marker 辅助注释。
关键参数: nFeature、nCount、percent.mt、PC 数和 resolution 根据数据调整。
输出结果: 质控后对象、cluster marker、细胞注释。
预期图表: QC 图、PCA/Elbow、UMAP/t-SNE、marker 热图，PNG/PDF，Times New Roman。
质控与调整策略: 注释不明确时列出候选 marker 并放入需确认信息。

## WGCNA
目的: 在 bulk 表达数据中识别与表型或评分相关的共表达模块。
输入: 表达矩阵、表型矩阵或通路评分。
方法与工具: R WGCNA。
关键参数: 软阈值优先选择 scale-free R2 >= 0.85；模块筛选常用 `|cor| > 0.3` 且 `P < 0.05`。
输出结果: 模块基因、关键模块、候选基因。
预期图表: 样本聚类树、软阈值图、模块树、模块-性状热图、GS-MM 散点图，PNG/PDF，Times New Roman。
质控与调整策略: 离群样本先剔除；模块基因过少时调整 MM/GS 阈值。

## hdWGCNA
目的: 在单细胞关键细胞群中识别共表达模块和 hub genes。
输入: 注释后的 Seurat 对象、关键细胞群、分组或表型。
方法与工具: hdWGCNA。
关键参数: metacell 构建；软阈值 scale-free R2 >= 0.85；模块相关性按原文或 `|cor| > 0.3` 且 `P < 0.05`。
输出结果: 模块、kME 排名基因、关键模块基因。
预期图表: 软阈值、模块树、模块相关图、模块 UMAP、kME 排名图，PNG/PDF，Times New Roman。
质控与调整策略: 细胞数不足时合并亚群或降低模块最小基因数。

## Cell Communication
目的: 推断细胞间配体-受体通讯变化。
输入: 注释后的单细胞对象和分组。
方法与工具: CellChat/CellPhoneDB；代谢物或神经递质通讯使用 MEBOCOST。
关键参数: 通讯显著性常用 `P < 0.05`；按疾病组与对照组分别分析。
输出结果: 通讯强度、互作次数、关键配体-受体或 sender-receiver 轴。
预期图表: circle plot、bubble plot、heatmap、Sankey 或 dot plot，PNG/PDF，Times New Roman。
质控与调整策略: 注释不稳会影响通讯结果；罕见细胞需谨慎解释。

## Machine Learning Diagnosis
目的: 从候选基因中筛选诊断标志物并评估模型性能。
输入: 候选基因表达矩阵、训练集分组、验证集分组。
方法与工具: LASSO、RF、SVM-RFE、XGBoost、GBM 或原文指定模型。
关键参数: 交叉验证常用 10-fold；AUC 标准按原文执行，未给出阈值时报告 AUC 并列入判断依据或需确认信息。
输出结果: 特征基因、生物标志物、模型性能。
预期图表: 模型重要性图、LASSO 曲线、Venn 图、ROC 曲线、表达箱线图，PNG/PDF，Times New Roman。
质控与调整策略: 模型交集为空时，将扩大候选基因或替换模型作为备选方案；只有原文允许或用户确认后才调整分析路线。

## PPI and Hub Genes
目的: 构建候选基因蛋白互作网络并筛选 hub genes。
输入: 候选基因列表。
方法与工具: STRING、Cytoscape、CytoHubba、MCODE。
关键参数: STRING score 常用 0.4，可按结果在 0.15-0.9 调整。
输出结果: PPI 网络、拓扑排名、hub genes。
预期图表: PPI 网络图、拓扑算法结果、Venn 图，PNG/PDF，Times New Roman。
质控与调整策略: 基因数过少时跳过拓扑交集或降低 STRING score。

## Pseudotime
目的: 分析关键细胞状态演化和关键基因动态表达。
输入: 关键细胞子集、分组、关键基因。
方法与工具: Monocle2/Monocle3 或原文指定工具。
关键参数: 起始状态根据对照组、健康状态或文献 marker 确定。
输出结果: 轨迹、分支、拟时序基因动态。
预期图表: 轨迹图、pseudotime 着色图、基因动态曲线、分支热图，PNG/PDF，Times New Roman。
质控与调整策略: 起点不明确时列入需确认信息。

## Localization and Regulatory Networks
目的: 解析关键基因调控关系和定位特征。
输入: 关键基因列表。
方法与工具: ChIPBase/JASPAR/ENCODE、TargetScan/miRDB/StarBase、GeneMANIA、Ensembl/NCBI/UCSC、HPA/mRNALocater。
关键参数: 使用原文数据库和阈值；无结果时切换备选数据库。
输出结果: TF/miRNA/circRNA 网络、GeneMANIA 网络、染色体定位、亚细胞定位。
预期图表: 调控网络图、GeneMANIA 图、染色体定位图、亚细胞定位图，PNG/PDF，Times New Roman。
质控与调整策略: 物种不匹配时先进行同源基因转换并标注风险。
