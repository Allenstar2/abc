# LDO 專題架構研究（0.18 µm CMOS，大學部專題）

這個目錄是一次自主研究的產出（2026-11-02）。**先讀 `REPORT.md` 第 a 節。**

| 檔案 | 內容 |
|---|---|
| `REPORT.md` | 最終報告（a 一頁結論 … j 參考文獻） |
| `APPLICATIONS.md` | 使用者追加：HBM、高速 SerDes 中的 LDO；PSRR 增強技術；供電漣波→jitter 模擬 |
| `ANALYSIS.md` | Stage 4：各架構小訊號模型、極零點、主導限制、失效情境；審查後的附錄 |
| `ARCH_MATRIX.md` | Stage 2：分類與比較矩陣 |
| `PAPER_SELECTION.md` | Stage 3：選文與排除理由（全部僅摘要） |
| `GAPS.md` | Stage 7：研究缺口（保留/刪除與理由） |
| `REVIEW_LOG.md`、`review/` | Stage 6：對抗審查紀錄與審查原文、審查者腳本 |
| `LEARNING.md`、`LEARNING_ANSWERS.md` | Stage 9：預測題、推導題、教授追問題、早上閱讀順序 |
| `DEVICE_CHAR.md` | PTM 180nm 元件特性（L=0.18/0.5/1 µm） |
| `literature.csv`、`REFERENCES.md`、`lit_raw/` | 文獻清單（93 列，全文狀態）、參考文獻、各 agent 原始紀錄 |
| `DECISIONS.md`、`STATE.md`、`LOG.md` | 假設與決定、目前狀態、時間記錄（只增不改） |
| `sim/` | netlist 產生器與實驗腳本（`sim/scripts/`）、結果（`sim/results/`）、圖（`sim/figs/`）、模型（`sim/models/`） |

**一鍵重跑**：`bash sim/run_all.sh`（需 ngspice ≥ 42、python3、numpy、matplotlib；資料集統計另需 pandas/openpyxl 與 `git clone https://github.com/mgseok/DLDO-survey ext/DLDO-survey`）。

證據標記：[M] 論文實測、[S] 論文模擬、[D] 推導、[X] 本次模擬（PTM 180nm，非真實製程）、[H] 假設或推測。
模型出處：`sim/models/MODEL_ATTRIBUTION.md`（PTM 180nm，CC BY 4.0 collection）。
