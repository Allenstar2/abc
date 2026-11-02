# DECISIONS（不確定時的合理假設；後續若被推翻，保留原文並加「更新」）

| ID | 決定 / 假設 | 理由 | 影響範圍 | 狀態 |
|---|---|---|---|---|
| D-001 | 所有產出放在 `Allenstar2/abc` repo 的 `ldo-research/` 子目錄，分支 `ccr-261645f3-hkvtpt` | `Allenstar2/Allenstar2` 是空 repo 且是 GitHub profile repo；對空 repo 推第一個分支會成為預設分支，README 可能直接顯示在個人頁面。`abc` 是測試用 repo，用子目錄隔離不影響既有 `index.html`。 | 檔案位置 | 有效 |
| D-002 | 規格假設：Vin=1.8 V、Vout=1.6 V（dropout 200 mV）、Imax ∈ {10, 50, 100} mA、on-chip CL ∈ {100 pF, 1 nF} | 使用者暫定規格，全部視為 [H]，做敏感度分析 | 全部分析 | 有效 |
| D-003 | 模型檔 `180nm_bulk.pm` 不修改；ngspice 會用 BSIM3v1 碼。已確認改 version=3.3.0 在單點 OP 結果相同，之後仍以原檔為準 | 避免「為了結果改模型」 | 模擬 | 有效 |
| D-004 | 模擬溫度預設 27 °C（模型 Tnom=27） | 與模型擬合溫度一致 | 模擬 | 有效 |
