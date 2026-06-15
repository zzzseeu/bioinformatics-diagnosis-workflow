rm(list = ls()); gc()
pwd <- "{{PROJECT_DIR}}"
res_folder <- "{{step_num}}_{{step_name}}"

setwd(pwd)

if (!dir.exists(paths = file.path(res_folder))) {
  dir.create(res_folder)
}

setwd(res_folder)

suppressPackageStartupMessages({
  library(Seurat)
  library(ggplot2)
})

input_10x_dir <- "{{INPUT_10X_DIR}}"
project_id <- "{{PROJECT_ID}}"
output_dir <- "."
counts <- Read10X(input_10x_dir)
obj <- CreateSeuratObject(counts = counts, project = project_id, min.cells = 3, min.features = 200)
obj[["percent.mt"]] <- PercentageFeatureSet(obj, pattern = "^MT-|^mt-")
qc_plot <- VlnPlot(obj, features = c("nFeature_RNA", "nCount_RNA", "percent.mt"), ncol = 3) +
  theme(text = element_text(family = "Times New Roman"))
ggsave(file.path(output_dir, "sc_qc_violin.png"), qc_plot, width = 9, height = 4, dpi = 300)
ggsave(file.path(output_dir, "sc_qc_violin.pdf"), qc_plot, width = 9, height = 4)
obj <- subset(obj, subset = nFeature_RNA > {{MIN_FEATURES}} & nFeature_RNA < {{MAX_FEATURES}} & percent.mt < {{MAX_PERCENT_MT}})
obj <- NormalizeData(obj)
obj <- FindVariableFeatures(obj, selection.method = "vst", nfeatures = 3000)
saveRDS(obj, file.path(output_dir, "seurat_qc_normalized.rds"))
