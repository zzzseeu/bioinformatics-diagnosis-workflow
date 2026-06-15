rm(list = ls()); gc()
pwd <- "{{PROJECT_DIR}}"
res_folder <- "{{step_num}}_{{step_name}}"

setwd(pwd)

if (!dir.exists(paths = file.path(res_folder))) {
  dir.create(res_folder)
}

setwd(res_folder)

suppressPackageStartupMessages({
  library(clusterProfiler)
  library(ggplot2)
  library({{ORG_DB}})
})

gene_list <- "{{GENE_LIST}}"
output_dir <- "."
org_db_name <- "{{ORG_DB}}"
genes <- scan(gene_list, what = character(), quiet = TRUE)
ego <- enrichGO(gene = genes, OrgDb = get(org_db_name), keyType = "{{KEY_TYPE}}", ont = "BP", pAdjustMethod = "BH")
write.csv(as.data.frame(ego), file.path(output_dir, "GO_BP_enrichment.csv"), row.names = FALSE)
p <- dotplot(ego, showCategory = 10) + theme(text = element_text(family = "Times New Roman"))
ggsave(file.path(output_dir, "GO_BP_dotplot.png"), p, width = 7, height = 5, dpi = 300)
ggsave(file.path(output_dir, "GO_BP_dotplot.pdf"), p, width = 7, height = 5)
