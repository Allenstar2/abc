# STATE（重新開始時先讀這個）

> 2026-11-02 17:2x 更新：使用者追加「HBM、高速 SerDes 用 LDO」研究，明天要看。輸出：lit_raw/agent5_hbm*、agent6_serdes*（待開）、APPLICATIONS.md（待寫）、sim/scripts/s10_vco_supply.py（待寫）。

- 目前階段：Stage 1 文獻（agent2 類比、agent3 數位/回顧仍在跑）＋ Stage 5 模擬（REF-A 完成，hybrid 待做）
- 已完成：Stage 0；DEVICE_CHAR.md；REF-A（s1–s4 腳本）；手算對照；邊沿時間實驗 X2
- 下一步：
  1. 建 hybrid（B 型）XSPICE 模型：實驗 X3（limit cycle vs dead band、時脈漣波、切換瞬間）
  2. 合併 lit_raw/*.csv → literature.csv；分類矩陣；PAPER_SELECTION.md
  3. Stage 4 分析文件 ANALYSIS.md
- 未解問題 / 阻礙：
  - 學術網站被網路政策擋 → 無全文（D-009）。Leduc 2025 = 未確認（D-010）
  - 下線平台、面積上限、時程未知 → 問教授
