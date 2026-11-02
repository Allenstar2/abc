# LEARNING_ANSWERS

數字來源：Part 1 的數字取自 `sim/results/learn_answers.json`（`python3 learn.py all`，[X]，PTM 180nm 只看趨勢）；Part 2 是推導 [D]（代入 [X] 的 OP 值）；Part 3 混合 [X]/[D]/[H] 與文獻摘要，各題分別註明。

## Part 1：10 題答案

**Q1 Cc（5 → 2 → 10 pF）**
| Cc | 零載 PM | 零載 UGF | 100 mA PM | 0→100 mA, 100 ns undershoot |
|---|---|---|---|---|
| 2 pF | 43.0° | 5.25 MHz | 82.9° | 229 mV |
| 5 pF | 66.4° | 2.45 MHz | 87.9° | 236 mV |
| 10 pF | 77.2° | 1.27 MHz | 89.5° | 280 mV |
重點：Cc 變小，GBW ≈ β·gm1/Cc 變大，但 p2 ≈ (G2+G_o)/CL 不變 → PM 掉。**undershoot 幾乎沒改善**（236→229 mV），因為大訊號時受 slew 與輕載起步限制，不是小訊號頻寬。「把頻寬拉高就能改善暫態」是常見錯誤直覺。

**Q2 pass W（2 / 4 / 8 mm）**
| W | dropout @100 mA | 滿載 DC 迴路增益 | 零載 PM | undershoot |
|---|---|---|---|---|
| 2 mm | 184 mV | 22.6 dB | 68.8° | 284 mV |
| 4 mm | 94 mV | 33.7 dB | 66.4° | 236 mV |
| 8 mm | 48 mV | 43.4 dB | 61.2° | 254 mV |
重點：W 加倍，dropout 約減半、滿載 triode 變淺（gm_p/gds_p 變大）→ 迴路增益回升 ~10 dB；但閘極電容也加倍 → buffer 極點下降、零載 PM 掉。**2 mm 的 dropout 184 mV 已經貼著 200 mV 規格**，只要溫度或製程一偏就掉出調節。undershoot 最小在中間（4 mm）：太小沒有電流餘裕，太大閘極太慢。

**Q3 CL 100 pF → 1 nF，Cc 不改**
零載 PM 66.4° → **29.8°**；1 mA 時 83.0° → 58.4°；100 mA 時 87.9° → 87.0°。只有輕載受傷，因為 p2 ≈ gm_p/CL 只有在 gm_p 小時才會落到 UGF 附近。

**Q4 洩放 50 / 200 / 500 µA**
零載 PM 37.8° / 66.4° / 78.1°；Iq 131 / 287 / 589 µA。弱反轉 gm_p ≈ I/(nU_T)，洩放加 4 倍 → p2 約加 4 倍。這是用 Iq 換穩定度。

**Q5 EA tail 10 / 20 / 40 µA**
零載 PM 76.0° / 66.4° / 53.9°；零載 UGF 1.41 / 2.45 / 3.89 MHz；undershoot 277 / 236 / 230 mV。tail 加倍 → gm1 增加 → GBW 增加 → PM 掉；EA 的 slew（I_tail/Cc）也增加，所以 undershoot 從 10→20 µA 改善明顯，20→40 µA 就飽和了（瓶頸換到別處）。

**Q6 起點電流（1 ns 邊沿）**
0 / 1 / 10 mA → 742 / 627 / 452 mV。起點越輕，pass 越接近關斷、gm_p 越小、閘極要擺越遠。**論文沒寫起點電流的 ΔV 不能比**。

**Q7 邊沿**
1 ns / 100 ns / 1 µs → 742 / 236 / 111 mV。ΔI·t/CL 只對「t 小於迴路反應時間」的快邊沿有意義：1 ns 時 ΔI·t_edge/CL = 1 V，量到 742 mV（pass 的 Vsd 變大會自己多給電流，加上 Cc、Cgd 的快速耦合）。

**Q8 溫度 125 °C、零外部負載**
Vout 1.6061 → 1.6140 V（+8 mV），pg 1.595 → 1.712 V。高溫 Vth 下降、漏電上升，pass 需要更高的閘極電壓才能只送 200 µA，EA 必須擺得更高，迴路增益剩下的誤差變大。在「SF-like」corner（|Vthp| −50 mV）125 °C 時 Vout = 1.6525 V，已失去調節（`s6_corners.py`）。

**Q9 hybrid 窗口（負載 20 mA）**
寬窗：0 次切換、Vout p-p 0 mV；窄窗：最後 5 µs 有 14 次切換、Vout p-p 216 mV。原因見 H3。

**Q10 PSRR@1 kHz（70 mA）**
REF-A −38.2 dB；REF-B（5 片導通）−18.8 dB，差 19 dB。導通的 slice 是 Vin→Vout 的低阻抗開關（triode，5 片合計約 0.3 S），而且讓 R_o 變小 → 類比迴路 DC 增益只剩 18.7 dB（REF-A 在 50 mA 為 43.4 dB、100 mA 為 33.7 dB；`x3d_hybrid_loop_frozen.json`、`s3_refA_char.json`）。

---

## Part 2：推導解答

### H1
- G_ea = 1.15 + 1.23 = 2.38 µS → gm1/G_ea = 77.3
- A_SF = 918 / (918 + 22 + 65.6) = 0.913；G2 = 0.913 × 4.98 mS = 4.55 mS
- G_o = 253 µS + 1/8 kΩ = 378 µS → gm_p/G_o = 13.2
- **T0 = 0.5 × 77.3 × 0.913 × 13.2 = 465 → 53.3 dB**（模擬 53.0 dB，線性差約 4%）
- p2 ≈ (G2+G_o)/CL = 4.93 mS / 100 pF = 4.93×10⁷ rad/s → **7.84 MHz**
- GBW ≈ β·gm1·G2 / [Cc(G2+G_ea+G_o)] = 0.5×184µ×4.55m / (5p×4.93m) = 1.68×10⁷ rad/s → **2.67 MHz**
- 兩極點下 |T|=1：f·√(1+(f/7.84)²) = 2.67 → f ≈ 2.54 MHz；相位 −90° − atan(2.54/7.84) = −108° → PM ≈ 72°
- 扣 buffer 極點 atan(2.54/29) ≈ 5°、RHP zero atan(2.54/144) ≈ 1° → **PM ≈ 66°**（模擬 66.4°，UGF 2.45 MHz）

### H2
- 開迴路：v_out = gds_p·v_in·R_o（pg 跟 Vin，所以 v_sg = 0）。閉迴路除以 (1+T0)：**PSRR ≈ gds_p·R_o/(1+T0)**。
- 100 mA：R_o = 1/(0.26 + 0.000125) ≈ 1/gds_p → gds_p·R_o ≈ 1；T0 = 33.7 dB = 48.4 → PSRR ≈ 1/49.4 = **−33.9 dB**（模擬 −33.3 dB）。
- 補充（第 1 輪審查）：pg 實際只跟到 Vin 的 α_pg = 0.948–0.994，精確式為 R_o·[gds_p + gm_p(1−α_pg)]/(1+T0)，近似式偏樂觀 0.6–2.2 dB。
- 若 pg 跟著 ground：v_sg = v_in，注入電流變成 (gm_p+gds_p)·v_in → 多乘 (gm_p+gds_p)/gds_p：100 mA 時 = 2.33（**差 7.4 dB**）；零載時 (gm_p+gds_p)/gds_p = (4.98+0.253)/0.253 ≈ 21 倍（**差約 26 dB**）。這就是為什麼 PMOS pass 的驅動電路要「以 Vin 為參考」。

### H3
1. 穩定碼 k 需要 I_L − k·I_s ∈ [I_a(VH), I_a(VL)]（寬度 W）。k 每加 1，類比電流跳 I_s。若 W < I_s，序列 {I_L − k·I_s} 可能整個跳過窗口：每個長度 I_s 的週期裡有 (I_s − W) 長的負載區間沒有任何穩定碼 → 碼在相鄰兩值間來回 = limit cycle。
2. 窄窗 W=[8, 14] mA、I_s=12.2 mA：洞在 I_L − 12.2k ∈ (14, 20.2)，即 **(14, 20.2)、(26.2, 32.4)、(38.4, 44.6)、(50.6, 56.8)、(62.8, 69.0)、(75.0, 81.2)、(87.2, 93.4)、(99.4, …)** mA；約一半負載範圍（(12.2−6)/12.2 = 51%）會 limit cycle。X3a 量的 20 mA 在洞裡，45/70/95 mA 不在（45−36.6=8.4、70−61=9、95−85.4=9.6 mA，都在窗內）。
3. 3→18 mA 段平均斜率 = 15 mA / 0.235 V = 63.8 mA/V → 一片 = 12.2/63.8 = **191 mV**。兩顆比較器 offset 差的 σ = √2 × 5 = 7.1 mV，3σ = 21 mV → **窗口 ≥ 212 mV（≈ 13.5 mA）**。本次寬窗 235 mV 只多 23 mV（約 3.3σ），**很緊**；再加上溫度讓 I–V 曲線平移，實作要再加寬或把 slice 做小。
4. （第 1 輪審查追加）若比較器後面有 d 級 DFF 同步器（防 metastability），決策延遲 d 個時脈，分界點變成 d+1：電路級 1 級同步器時寬窗有 11/31、2 級同步器 26/31 負載點 limit cycle；shift register 改每 d+1 個時脈更新一次即全部消失（`s13_hybrid_sync.py`）（初版接法錯誤：shift register 時脈晚 1 ns 使第 2 級同步器透明，量到的 11/31 其實是 d=1；第 2 輪 (c) 指出後更正）。

---

## Part 3：20 題教授追問答案

1. **主極點在 EA 輸出（ea 節點）**。Cc 從 Vout 跨到 ea，被第二級增益 A2 = A_SF·gm_p·R_o 放大（Miller），p1 ≈ G_ea·G_o/[Cc(G2+G_o)]。capless 時 CL 只有 100 pF–1 nF，若讓輸出當主極點，滿載 UGF ≈ β·A_EA·gm_p/CL 會到 GHz 級，內部節點跟不上。
2. 非主極點 p2 ≈ (G2+G_o)/CL，弱反轉 gm_p ≈ I/(nU_T)，最輕載時最低；GBW ≈ β·gm1/Cc 幾乎不隨負載變 → 輕載時 p2/GBW 最小。數字：零載 p2 = 7.8 MHz、GBW = 2.6 MHz；10 mA 時 p2 = 270 MHz。
3. 要看補償，而且要看角落。純 Miller（無 Rz）時 1 nF 要 Cc=20 pF，100 ns 邊沿 346 mV vs 100 pF 的 236 mV。第 1 輪審查用 Rz=10 kΩ 讓 1 nF 變成 431/185/80 mV（看似全面勝出），但第 2 輪審查發現 Rz=10 kΩ 在 FF −40 °C＋Ibias+30%＋Cc 底板寄生下 PM 掉到 −5°（振盪）。穩健的小 Rz（3 kΩ）下 1 nF 是 468/234/112 mV：只在 1 ns 快邊沿占優。結論：**加大 CL 只對快邊沿有幫助；補償選擇必須跑角落**（ANALYSIS 附錄、`s16_rz_robust.py`）。
4. Triode。100 mA、Vsd=0.2 V：gm_p=347 mS、gds_p=260 mS，gm_p/gds_p=1.33。迴路增益 53→33.7 dB，PSRR@1 kHz −55→−33 dB。
5. 定義：Vout 掉到「Vin 足夠高時的穩態值」的 99% 時的 Vin−Vout。REF-A 100 mA 時 94 mV、50 mA 時 48 mV；規格 200 mV → 餘裕約 100 mV，但沒有考慮 corner 與 pass 的金屬/封裝電阻（100 mA × 0.5 Ω = 50 mV [H]）。
6. 必要：EA tail 20 µA、buffer ~50 µA、偏壓 20 µA；洩放 200 µA 是為了輕載穩定（Q4）。拿掉要換 adaptive bias（EA 電流隨負載）或其他補償；代價是設計複雜度與 adaptive 迴路自身的穩定性。
7. 片上 NMOS 負載陣列＋inverter 驅動；邊沿目標 ~1 ns 與 100 ns 兩檔；外部負載因 bond wire L·di/dt（1 nH×100 mA/1 ns = 100 mV）與探棒電容，邊沿慢且會汙染 Vout。Vout 用直接 sense pad＋高阻抗主動探棒（第 3 輪審查模擬看到真值的 100–103%，片上 buffer 反而要 ≥3 mA 才有 97%），所以最小可行晶片不放監測 buffer。**量測板不能在 Vout 腳放去耦電容**：模擬 1 nF/10 nF 板上電容讓最差 PM 掉到 28.7°/18.2°（`s18_offchip_cap.py`）。（若真的要放監測 buffer，看清 1 ns 邊沿需 3–10 mA 偏壓，審查者估。）
8. FoM 不含邊沿時間、起點電流、CL 定義不一致。例：同一顆 X. Wang CICC 2019，1 ns 邊沿 185 mV、10 ns 邊沿 88 mV（Seok 資料集）；本次 REF-A 同電路 0→100 mA 從 748 mV（0.1 ns）到 111 mV（1 µs），起點 10 mA 時只剩 21 mV。
9. z = G2/Cc（RHP）：零載 144 MHz、滿載 10 GHz。只有 G2 很小（極輕載）或 Cc 很大時才會靠近 UGF；本設計零載只扣 ~1°。可加 nulling 電阻 Rz 移到 LHP。
10. Source follower 把 pg 節點的阻抗降到 ~1/gm_b（~1 kΩ），pg 極點推到 20–30 MHz。**不對稱**：PMOS SF 往下拉靠 SF 電晶體（強），往上拉只靠 50 µA 電流源（50 µA/7.9 pF ≈ 6.3 V/µs），所以卸載 overshoot 回復慢。
11. 不行。REF-A 100 mA 時 TT 27 °C 下 Vin=1.674 V 已掉 1%，SS 125 °C 下 1.716 V 就掉（Vin 只降 4.7%）。若 Vout 改 1.4 V，最低 Vin 變 1.508/1.560 V，滿載迴路增益多 15 dB、PSRR@1 kHz 好 13 dB（`s17_spec_alt.py`）。要問教授 Vin 的來源、容差與 Vout 是否可調。
12. 中頻（UGF 附近 1–3 MHz）最差，接近 0 dB；高頻靠 CL 分流，但滿載 gds_p/(2πCL) 轉折在 ~400 MHz，所以 10–100 MHz 都在 0 dB 附近。改善：增加 EA 增益與頻寬、feedforward ripple cancellation（Park 2014 的方向）、NMOS pass（需 charge pump）、加大 CL。
13. 會。條件是窗口電流 > 一片電流（加比較器 offset 與溫漂餘裕），否則約一半負載範圍會 limit cycle（H3、X3a）；若加了 d 級同步器，還要每 d+1 個時脈才更新（`s13`）；另外卸載時類比迴路飽和下仍移除 slice 會自造 ~530 mV 下陷（`s20`），DN 要等類比迴路脫離飽和。另外每次切換是一次 12 mA 的快速負載步階，造成 34–83 mV 尖峰（依 slice 邊沿）。
14. **未確認**。只讀到摘要：有「transient response is dictated by the digital portion」與數位逼近演算法等偏 C 線索，但穩態誰供電、DC 精度誰決定、數位穩態是否停止都沒寫。要讀全文或 Leduc 的碩士論文才能判定。
15. 用閘級：雙向 thermometer shift register 每位元＝1 DFF＋3 AND2＋1 OR3（本次 XSPICE 就是這個結構）；比較器用連續比較器＋2 級 DFF 同步器，**而且 shift register 要每 3 個時脈才更新一次**（否則同步器延遲會造成 limit cycle：`s13` 電路級 2 級同步器 26/31 負載點振盪 → 加 ÷3 後 0/31）；時脈從外部輸入。驗證：LTspice 電晶體級跑代表性情境（加片、減片、hold、上電）。XSPICE 沒有 metastability 與 setup/hold 違規，要另外用電晶體級檢查。
16. 只能看趨勢。lmin=lmax=0.18 µm 代表 L≠0.18 µm 是外插；本次量到 gm/gds 隨 L 增加（NMOS 12→59→97）方向合理，但 Vth 對 L 不單調（0.41→0.50→0.45 V）。而且沒有 corner、沒有 mismatch 模型。下線前一定要換成平台的 PDK 重做。
17. PMOS pass 只能「送」電流不能「吸」電流。卸載時多餘的電流只能靠洩放或 pass 關斷後的漏電慢慢放電：1 nF × 0.2 V / 200 µA = 1 µs；而且 Vout 可能直接衝到 Vin（本次 100 pF 時 overshoot 被 Vin 夾在 206 mV）。
18. 不一定。本次 class-B 電容耦合 SRE：小訊號完全不變（PM、PSRR 相同），最佳參數下 undershoot 只改善 8–15%，參數掃描中 100 ns 邊沿最差從 236 惡化到 348 mV（+48%，過度修正後振鈴；`x4b_sre_sweep.json`）；第一版偏壓還因 PTM PMOS 的 DIBL 讓偵測管靜態導通，整顆 LDO 失效（LOG.md）。
19. 要做：PDK 的 TT/FF/SS/FS/SF × −40/27/125 °C × Vin 範圍；mismatch Monte Carlo（EA offset → Vout 精度；hybrid 比較器 offset → 窗口）；佈局後寄生（pass device 的金屬電阻、pg 節點電容）；ESD 與 latch-up。本次只做了 Vth ±50 mV、Tox ±5%、溫度三點的粗略擾動，沒有 mismatch、沒有佈局。
20. 誠實說：架構本身不新。可能的小貢獻是 GAPS.md G1——在同一顆 0.18 µm capless LDO 上，用片上可程式負載與直接 sense pad，系統化量測 ΔV 對邊沿時間、起點電流、取出方式的依賴，說明 FoM 排名如何被量測條件改變。已有人做過兩種邊沿的比較（X. Wang CICC 2019），所以要定位為「量測方法學的整理」。
