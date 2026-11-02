# DECISIONS（不確定時的合理假設；後續若被推翻，保留原文並加「更新」）

| ID | 決定 / 假設 | 理由 | 影響範圍 | 狀態 |
|---|---|---|---|---|
| D-001 | 所有產出放在 `Allenstar2/abc` repo 的 `ldo-research/` 子目錄，分支 `ccr-261645f3-hkvtpt` | `Allenstar2/Allenstar2` 是空 repo 且是 GitHub profile repo；對空 repo 推第一個分支會成為預設分支，README 可能直接顯示在個人頁面。`abc` 是測試用 repo，用子目錄隔離不影響既有 `index.html`。 | 檔案位置 | 有效 |
| D-002 | 規格假設：Vin=1.8 V、Vout=1.6 V（dropout 200 mV）、Imax ∈ {10, 50, 100} mA、on-chip CL ∈ {100 pF, 1 nF} | 使用者暫定規格，全部視為 [H]，做敏感度分析 | 全部分析 | 有效 |
| D-003 | 模型檔 `180nm_bulk.pm` 不修改；ngspice 會用 BSIM3v1 碼。已確認改 version=3.3.0 在單點 OP 結果相同，之後仍以原檔為準 | 避免「為了結果改模型」 | 模擬 | 有效 |
| D-004 | 模擬溫度預設 27 °C（模型 Tnom=27） | 與模型擬合溫度一致 | 模擬 | 有效 |
| D-005 | 參考 LDO（REF-A）拓樸：NMOS 輸入 5T OTA → PMOS source follower（body 接 source）→ PMOS pass (L=0.18 µm)，Miller Cc 由 Vout 接到 EA 輸出；Vref=0.8 V 理想源、偏壓電流 10 µA 理想電流源 | 最簡單、可手算、學生在 LTspice 也能重建；NMOS 輸入對讓 EA 輸出能拉到 ~1.6 V 以關閉大 pass device | 所有 [X] 結果 | 有效 |
| D-006 | Pass device W 依 Imax 縮放：10 mA → 400 µm、50 mA → 2000 µm、100 mA → 4000 µm（L=0.18 µm） | 由 DEVICE_CHAR.md：Vsd=0.2 V、Vg≈0.9 V 時約 43 mA/mm，留 ~1.7× 餘裕 | 面積、閘極電容、dropout | 有效 |
| D-007 | 負載用理想電流源（不是電阻） | LDO 量測常用電流負載；電阻負載會讓 R_out 變小、PM 變好，會美化結果 | 迴路增益、暫態 | 有效 |
| D-008 | 最小負載（分壓器電流）取 200 µA（R1=R2=4 kΩ）；CL=100 pF 用 Cc=5 pF，CL=1 nF 用 Cc=20 pF | `s1_refA_sweep.py` 掃描：Imin=50 µA 時任何 Cc≤40 pF 在 CL=1 nF 下 PM≤41°；Imin=200 µA + 上述 Cc 讓最差 PM 達 66°(100 pF)/55°(1 nF)。代價是 Iq 增加約 150 µA。**這是工程取捨不是最佳化**，adaptive biasing 可降 Iq 但增加複雜度 | Iq、PM、暫態 | 有效 |
