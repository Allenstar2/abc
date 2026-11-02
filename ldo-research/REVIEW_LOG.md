# REVIEW_LOG（對抗審查紀錄）

每輪開全新 subagent，不給作者推理過程，只給 repo 內容。原始審查報告在 `review/`。

## 第 1 輪（2026-11-02）

### (b) 引用與數字抽查 — `review/round1_b_citation_check.md`
- 共查 128 項（文獻 60、模擬 68）：一致 97、不一致 11、標記錯誤 12、無法查證 8。
- **已修正**（同日）：
  - 不一致：D02 dropout 300→200 mV；Tang 2018 CL 改為摘要 20 pF（資料集算 FoM 用 30 pF）、補 ΔI 90 mA、id 改 X01-r22；0.18 µm Vin 範圍改 0.7–5 V；dead-zone 引用改 H08；排除筆數 44→43；C_gg 5.3→5.5 pF（原值屬舊設計）；ΔV_g 0.52→0.47 V、I_drive 0.8→0.75 mA；REF-A 95 mA Vout 1.5932→1.5936 V；PSRR@1 MHz 範圍改 −5.3～−8.7 dB；REF-B Imax 改 ≈131 mA（類比部分實測 33 mA，`s11_misc_checks.py`）。
  - 標記錯誤：推得的 dropout/面積加 [D]；H11 Imax 改「—（ΔI=200 mA）」；厚氧改 [H]；A06「只多幾顆電晶體」改 [H，待全文]；A12 DOI 加「未驗證」；DEVICE_CHAR 標題「實測」→「模擬」、漏電對 Vin 敏感改 [D/H]；時脈饋通改 [H]（未模擬）；B 的設計規則改標 [D]/[H] 並寫明模擬只驗過 1.23× 與 0.49×。
  - 無法查證：補 `s11_misc_checks.py` 存檔 BSIM v3.1/v3.3.0 比較、1 nF overshoot 回復 2.2 µs（原寫「約 1.5–2 µs」，已更正）、REF-B 類比最大 33 mA 與 Iq 289 µA、500 µA 洩放公平性表。
- **對結論的影響**：數字修正不改變方向；但審查者指出 `x4_sre.json` 顯示 SRE 讓 100 ns undershoot 從 235.5 惡化到 283.8 mV，與結論草稿「首選＝A＋SRE」相衝 → 列入結論修訂（見本輪結論變動）。
