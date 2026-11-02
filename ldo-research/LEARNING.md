# LEARNING：讓你真的學會（不是看懂而已）

使用方式：每一題**先寫下你的預測（數字或方向＋一句理由）**，再去看 `LEARNING_ANSWERS.md` 與跑模擬。
預測錯了最有價值——把錯的原因寫在旁邊。

所有實驗以 REF-A 為基準：NMOS 輸入 5T OTA → PMOS source follower → PMOS pass（W=4 mm, L=0.18 µm），
Miller Cc=5 pF（Vout→EA 輸出），CL=100 pF，洩放 200 µA（R1=R2=4 kΩ），Vin=1.8 V、Vout=1.6 V。電路在 `sim/scripts/ldo_ref.py`。
執行環境：`cd ldo-research/sim/scripts`，需要 ngspice 與 python3（numpy、matplotlib）。

---

## Part 1：10 題「先預測再看答案」

| # | 改變什麼（其他不變） | 請預測 | 模擬指令 |
|---|---|---|---|
| Q1 | Cc：5 pF → 2 pF、→ 10 pF | 零載 PM、零載 UGF、0→100 mA（100 ns 邊沿）undershoot 各往哪走？undershoot 會大幅改善嗎？ | `python3 learn.py Q1` |
| Q2 | pass W：4 mm → 2 mm、→ 8 mm | dropout（100 mA）、滿載 DC 迴路增益、零載 PM、undershoot | `python3 learn.py Q2` |
| Q3 | CL：100 pF → 1 nF，**但 Cc 不改** | 零載 PM 變多少？1 mA、100 mA 的 PM 呢？（延伸：再加 Rz=10 kΩ、Cc=8 pF 會怎樣？見 ANALYSIS.md 附錄） | `python3 learn.py Q3` |
| Q4 | 洩放電流：200 µA → 50 µA、→ 500 µA | 零載 PM 與 Iq | `python3 learn.py Q4` |
| Q5 | EA tail 電流：20 µA → 10 µA、→ 40 µA | 零載 PM、UGF、undershoot | `python3 learn.py Q5` |
| Q6 | 負載步階起點：0 → 1 mA → 10 mA（終點都 100 mA，1 ns 邊沿） | undershoot | `python3 learn.py Q6` |
| Q7 | 邊沿：1 ns → 100 ns → 1 µs（0→100 mA） | undershoot；哪一個最接近「ΔI·t/CL」的估計？ | `python3 learn.py Q7` |
| Q8 | 溫度：27 °C → 125 °C，零外部負載 | Vout 會上升還是下降？為什麼？ | `python3 learn.py Q8` |
| Q9 | hybrid（REF-B）數位窗口：3–18 mA（寬）→ 8–14 mA（窄），一片 slice = 12.2 mA，負載 20 mA | 會不會 limit cycle？p-p 多大？ | `python3 learn.py Q9` |
| Q10 | 70 mA 時 PSRR@1 kHz：REF-A vs REF-B（5 片 slice 導通、碼凍結） | 哪個好？差幾 dB？為什麼？ | `python3 learn.py Q10` |

全部一起跑：`python3 learn.py all`（約 1 分鐘），結果寫在 `sim/results/learn_answers.json`。

---

## Part 2：3 個要親手推導的小題（不要先看答案）

### H1. REF-A 的 DC 迴路增益與 UGF
給定零外部負載的 OP（ngspice 擷取）：gm1 = 184 µS，gds2 = 1.15 µS，gds4 = 1.23 µS，gm_b = 918 µS，gds_b ≈ 22 µS，gds_cs = 65.6 µS，gm_p = 4.98 mS，gds_p = 253 µS，R1+R2 = 8 kΩ，β = 0.5，Cc = 5 pF，CL = 100 pF，C1 ≈ 50 fF。
1. 推 T0 = β·(gm1/G_ea)·A_SF·(gm_p/G_o)，算出 dB 值。
2. 推非主極點 p2 ≈ (G2+G_o)/CL（G2 = A_SF·gm_p）與 GBW ≈ β·gm1·G2/[Cc(G2+G_o)]，換成 MHz。
3. 只用 GBW 與 p2 估 PM（先忽略 buffer 極點與 RHP zero），再說明 buffer 極點（約 29 MHz）會再扣多少度。
4. 跟模擬比：53.0 dB、UGF 2.45 MHz、PM 66.4°。

### H2. 低頻 PSRR
假設 pass 閘極完全跟著 Vin 走（v_pg = v_in），Vin 的小訊號 v_in 只經 gds_p 注入輸出。
1. 寫出開迴路 v_out/v_in，再用回授求閉迴路 PSRR ≈ gds_p·R_o/(1+T0)。
2. 用 100 mA 的值（gm_p = 347 mS、gds_p = 260 mS、T0 = 33.7 dB、負載是理想電流源）算 PSRR。
3. 如果 pg 不是跟著 Vin，而是跟著 ground（例如 EA 的 mirror 接 ground 那一側），PSRR 會變好還是變差？大約差多少？

### H3. 類比主導 hybrid 的 dead band
類比 pass（800 µm）在 Vsd = 0.2 V 時的 I–V(pg)：3 mA @1.39 V、8 mA @1.30 V、14 mA @1.21 V、18 mA @1.155 V；一片 slice = 12.2 mA。
1. 證明：若 I_a(VL) − I_a(VH) < I_slice，必存在某些負載沒有穩定碼。
2. 窄窗（VH=1.30、VL=1.21）時，哪個負載區間會 limit cycle？用 0–100 mA 列出所有「洞」。
3. 假設 [H] 比較器 offset σ = 5 mV（兩顆獨立；實際要用 PDK mismatch 模型估），要 3σ 不出洞，窗口（電壓）最少要多寬？換成電流大約多少？（用 3→18 mA 區段的平均斜率 dI/dV）

---

## Part 3：20 題教授可能追問的問題（答案在 LEARNING_ANSWERS.md）

1. 你的 LDO 主極點在哪個節點？為什麼不是輸出節點？
2. 為什麼最輕載是 PM 最差的地方？給公式。
3. CL 從 100 pF 加到 1 nF，暫態一定變好嗎？
4. 你的 pass device 在滿載時是飽和還是 triode？這對 loop gain、PSRR 有什麼影響？
5. Dropout 怎麼定義？你量的是哪個定義？200 mV 規格下你的餘裕多少？
6. Iq 裡面哪些是必要的？洩放電流 200 µA 能不能拿掉？代價是什麼？
7. 負載暫態你要怎麼在晶片上量？邊沿時間多少？為什麼不能用外部電子負載？
8. 為什麼不同論文的 FoM 不能直接比？舉一個具體例子。
9. RHP zero 在哪裡？什麼條件下會傷害 PM？
10. 為什麼用 source follower 驅動 pass gate？它對上拉與下拉的 slew 是對稱的嗎？
11. 如果 Vin 是 1.8 V ±10% 的外部電源，你的 LDO 在 1.62 V 還能調節嗎？
12. PSRR 在哪個頻段最差？為什麼？要改善有哪些方法？
13. Hybrid LDO 的數位迴路和類比迴路會不會打架？你怎麼保證不 limit cycle？
14. Leduc 2025 是 B 還是 C？你怎麼判斷的？
15. 沒有 Verilog，數位部分你要怎麼實作與驗證？
16. 你的模擬模型可信嗎？lmin=lmax=0.18 µm 對長通道元件有什麼影響？
17. 為什麼 capless LDO 的 overshoot 常比 undershoot 難處理？
18. Slew-rate enhancement 一定會改善暫態嗎？有什麼副作用？
19. 下線前你要做哪些 corner/溫度/蒙地卡羅檢查？哪些是本次沒做到的？
20. 這個題目你的「貢獻」是什麼？跟直接重做一篇論文有什麼差別？

---

## Part 4：早上 30 分鐘閱讀順序

| 時間 | 讀什麼 | 目的 |
|---|---|---|
| 0–5 分 | `REPORT.md` 第 a 節（一頁結論）＋第 h 節（要問教授的問題） | 先知道建議與你要做的決定 |
| 5–10 分 | `DECISIONS.md` 全部（尤其 D-002、D-008、D-009、D-010） | 知道哪些是假設、哪些被網路限制卡住 |
| 10–17 分 | `ANALYSIS.md` A1 節（小訊號模型＋手算 vs 模擬表）＋B 節的 X3a 表 | 這兩段是教授最可能深挖的電路細節 |
| 17–22 分 | 圖：`sim/figs/s3_refA_load_tr.png`、`x2_edge_time.png`、`x3a_limit_cycle.png` | 用眼睛確認三個關鍵主張 |
| 22–27 分 | `REVIEW_LOG.md` | 看哪些結論被審查者推翻或修正過 |
| 27–30 分 | 本檔 Part 1 挑 Q3、Q6、Q9 先寫預測 | 帶著問題去跟教授討論 |
