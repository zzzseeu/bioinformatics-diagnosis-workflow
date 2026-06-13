suppressPackageStartupMessages({
  library(limma)
  library(ggplot2)
  library(pheatmap)
})

expression_matrix <- "{{EXPRESSION_MATRIX}}"
group_metadata <- "{{GROUP_METADATA}}"
group_column <- "{{GROUP_COLUMN}}"
case_label <- "{{CASE_LABEL}}"
control_label <- "{{CONTROL_LABEL}}"
output_dir <- "{{OUTPUT_DIR}}"

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
expr <- read.csv(expression_matrix, row.names = 1, check.names = FALSE)
meta <- read.csv(group_metadata, check.names = FALSE)
stopifnot("sample" %in% colnames(meta))
stopifnot(group_column %in% colnames(meta))
expr <- expr[, meta$sample, drop = FALSE]
design <- model.matrix(~ 0 + factor(meta[[group_column]], levels = c(control_label, case_label)))
colnames(design) <- c("control", "case")
fit <- lmFit(expr, design)
contrast <- makeContrasts(case - control, levels = design)
fit2 <- eBayes(contrasts.fit(fit, contrast))
deg <- topTable(fit2, number = Inf, adjust.method = "BH")
write.csv(deg, file.path(output_dir, "DEG_results.csv"))

deg$gene <- rownames(deg)
deg$significant <- deg$adj.P.Val < 0.05 & abs(deg$logFC) > 0.5
p <- ggplot(deg, aes(logFC, -log10(adj.P.Val), color = significant)) +
  geom_point(size = 1) +
  theme_bw(base_family = "Times New Roman")
ggsave(file.path(output_dir, "DEG_volcano.png"), p, width = 7, height = 5, dpi = 300)
ggsave(file.path(output_dir, "DEG_volcano.pdf"), p, width = 7, height = 5)

top_genes <- head(rownames(deg), 30)
png(file.path(output_dir, "DEG_top_heatmap.png"), width = 1800, height = 1600, res = 300)
pheatmap(expr[top_genes, , drop = FALSE], fontsize = 8, family = "Times New Roman")
dev.off()
pdf(file.path(output_dir, "DEG_top_heatmap.pdf"), width = 7, height = 6, family = "Times")
pheatmap(expr[top_genes, , drop = FALSE], fontsize = 8)
dev.off()
