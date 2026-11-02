# LDO 專題架構研究報告（0.18 µm CMOS，大學部）

> 版本：2026-11-02（第 2 輪審查後初稿；第 3 輪審查與最終檢查的修改記在 `REVIEW_LOG.md`）
> 證據標註：[M] 論文實測、[S] 論文模擬、[D] 推導、[X] 本次模擬（PTM 180nm，**不是**真實製程，只看趨勢）、[H] 假設或推測。
> **最重要的限制**：本次 session 的網路政策擋掉所有學術網站，**literature.csv 93 列中，92 篇文獻只讀到搜尋摘錄（僅摘要）**；唯一實際開啟的是 X01（Seok 等人的 DLDO survey 資料集，屬二手整理）。DOI 未經 doi.org 解析（DECISIONS D-009）。所以本報告的電路判斷以 [D]/[X] 為主，文獻只當方向與數字參考。

---

## a. 一頁結論

| 項目 | 結論 |
|---|---|
| **先決條件** | **規格要先和教授確認**。1.8 V→1.6 V、100 mA 是最脆弱的一環：SS-like 125 °C 時 100 mA 的最低可調節 Vin 是 1.716 V（只容許 −4.7%）[X，`s17`]。Vout 改 1.4 V 時容許 −13%、滿載迴路增益 +15 dB、PSRR@1 kHz +13 dB，**但卸載過衝從 206 mV 變 404 mV**（Vout 會衝到 Vin）[X，`s21`] |
| **預設方案（首選）** | **A：純類比 capless LDO**（教授沒有要求 hybrid 時）。基準：NMOS 輸入 EA → PMOS source follower → PMOS pass（L=0.18 µm），**純 Miller 補償（Rz=0）**、最小負載洩放（或 adaptive bias）、片上可程式負載。選 A 的理由是**首次下線的失效模式最少**，不是性能大幅領先。A 的類比核心就是 B 的類比迴路，**在確認教授意向前，用 PDK 重建 REF-A、跑角落、定補償這幾步兩條路共用** |
| **決策規則** | ① 教授沒有 hybrid 要求 → **A**。② 教授要「hybrid 元素」、接受低風險 → **B**（類比 pass ≈2.4 mm、寬窗、gate-sensing、同步器＋÷(d+1)、數位 reset 可降級成類比 LDO）。③ 教授要「做 Leduc 那種」→ 先說明 Leduc 依標題（"Analog Assisted"＝本報告分類的 C/AAD）與前作 H02 摘要（數位決定 power transistor 大小、類比 EA 只管零載/輕載）**很可能是 C**（仍未確認）；無 Verilog 時建議以 ② 代替，或參考同作者的**純類比雙迴路 capless LDO（H03，TSMC 180 nm）**走 A。④ 教授接受 Vout ≈ 1.0 V（簡單 5T EA 時 10 mA 的上限約 1.0 V；1.2 V 只能供 ≤2 mA），且 10 MHz 級 PSRR 或 1 ns 暫態是主要指標（HBM/SerDes 動機）→ **A 的 NMOS-pass 子類**（見 b.4；代價是 1 kHz PSRR 差 24–42 dB） |
| **排除** | **C：數位主導**。Vin 1.8 V 不缺類比 headroom、教授偏類比、學生無 Verilog；要贏暫態需要的非同步路徑在 B 上就已經很脆弱（審查者模擬，作者未重現） |
| **Leduc 2025** | **未確認（僅摘要）**。線索強烈偏 C（標題、"transient response is dictated by the digital portion"、H02 摘要），但穩態誰供電、DC 精度誰決定、數位穩態是否停止仍未讀到（D-010） |
| **信心程度** | 技術排序 A ≥ B：**中**——照本報告規則實作的 B（2 級同步器＋÷3）在 5→95 mA、100 ns 邊沿 undershoot 180 mV vs A 127 mV（+41%）、卸載後回到 ±1% 要 2.3 µs vs 0.145 µs（約 16 倍）[X，`s20`]；理想 B（無同步器）差 21%、回復慢 5.5 倍。PSRR 只在 ≤1 MHz 有限差距，文獻 hybrid 可做到好 PSR，不是理由。**最終選擇取決於教授意向——缺的是輸入，不是證據。** A vs C：就學生可行性而言**高**（C 未模擬）。所有絕對數字：**低**（PTM、無 PDK、無佈局） |
| **最大風險** | (1) 規格在角落下失去調節；(2) 1 ns 級快邊沿 100 mA 步階在 100 pF 下 undershoot >400 mV [X]，推測 0.18 µm 任何迴路都難 <200 mV [D/H]；(3) 模型不是真實製程；(4) **下線流程**：只有 LTspice，佈局、DRC/LVS、寄生抽取用什麼工具未知；ESD、latch-up、電遷移（100 mA）、熱、上電順序都未模擬 |
| **最弱的結論** | 「A 優於 B」的**理由**被三輪審查削弱多次（現在主要靠驗證風險、同步器規則下的暫態/回復、以及 B 卸載後 ~530 mV 的自造下陷）；B 加遮蔽式 droop 路徑後 undershoot 可能降到 59 mV（只有行為模型）——**若電路級成立，技術排序可能反轉**；B 非同步 droop 路徑脆弱（審查者模擬，可能含 XSPICE 假象）；NMOS-pass 子類的優缺點（審查者模擬）；所有文獻數字（92 篇僅摘要） |
| **會改變建議的新資訊** | 教授要 hybrid；Leduc 全文顯示為簡單 B；Imax ≥ 200–300 mA；Vin 可用 3.3 V；平台有標準元件庫且允許合成；PSRR/jitter 或 1 ns 暫態是主要指標且可降 Vout（→ NMOS-pass） |
| **HBM/SerDes** | 不改變首選類別，但改變評估指標：要量 PSRR 對頻率曲線與「供電漣波→jitter」；**不能宣稱做的是 HBM 或 SerDes 用 LDO**（HBM rail 0.4–1.2 V；SerDes 時脈 rail 是 mW 級）。詳見 `APPLICATIONS.md` |

---

## b. 架構概觀與比較矩陣

### b.1 分類（詳見 `ARCH_MATRIX.md`）
| 類 | 誰決定穩態 Vout | 誰供主要電流 | 誰負責快速暫態 |
|---|---|---|---|
| A 純類比 | 類比 EA | 類比 pass | 類比（Miller、buffer、SRE、FVF…） |
| B 類比主導 hybrid | 類比 EA | 類比＋數位 slice（數位只粗調） | 類比為主 |
| C 數位主導 | 數位（量化）＋類比細調 | 數位 slice | 數位為主 |

### b.2 本專題條件下的比較（[X] 為同一 PTM 模型、同 CL=100 pF）
| 準則 | A（REF-A，4 mm） | B（公平版，類比 2.4 mm＋8×130 µm slice） | C |
|---|---|---|---|
| 5→95 mA undershoot（1 ns/100 ns/1 µs） | 499/127/27 mV [X] | 理想（無同步器）553/154/33 mV；**照規則加 2 級同步器＋÷3：100 ns 時 180 mV** [X，`s12`、`s20`] | 未模擬 |
| 卸載後回到 ±1%（95→5 mA，100 ns 邊沿） | 0.145 µs [X] | 0.80 µs（理想）／**2.3 µs**（同步器＋÷3）[X，`s20`] | — |
| **卸載後的自造下陷**（slice 在類比迴路飽和時被逐片移除） | 0 mV [X] | **524–529 mV**（Vout 掉到 1.07 V，最後一片關掉時）[X，`s20`、`sim/figs/x7_B_release_dip.png`]；第 3 輪 (c) 電晶體級交叉檢查 0.13–0.6 V | — |
| PSRR@1 kHz（70 mA） | −38.2 dB [X] | −24.2 dB（碼 5，作者 [X]）～−30.1 dB（碼 3，審查者 [X]） | 資料集 8 列 @1 MHz：−5～−46 dB（中位 −27），多為專做 PSR 增強的 hybrid → **不能說 B/C 的 PSR 本質上較差** |
| PSRR 1 MHz / 10–100 MHz（70 mA） | −6.7 dB / ≈0 dB | −1.9～−4.1 dB / ≈0 dB（10–100 MHz 與 A 差 ≤0.6 dB；審查者 [X]） | — |
| 同條件 load reg（20→95 mA） | 6.1 mV [X] | 0.5 mV [X]（可能被 IR/熱蓋過 [H]） | — |
| 離散狀態風險 | 無 | 窗口 vs 片電流、比較器 offset、同步器延遲都可能 limit cycle [X] | 本質有 limit cycle |
| 數位實作（無 Verilog） | 不需要 | 8 DFF＋33 閘＋2 比較器（另加同步器 2d 個 DFF 與 ÷(d+1) 計數器），可手畫 [D] | 演算法控制通常要合成 [H] |
| 教授「偏類比」 | 符合 | 符合 | 不符 |

### b.3 文獻矩陣（僅摘要，跨論文不可比）
主要 0.18 µm 例子：A01 Park 2014 JSSC（PSR 優於 −56 dB 至 4 MHz @50 mA [M]）、A05 Limpisawas 2022（0–100 mA、CL 0–1 nF、Iq 14 µA）、F03 Kao 2024（0.1→100 mA、100 ns 邊沿 <43.5 mV [M]，Vin 1.8–3.3 V）、F04 Kao 2022（0→100 mA、100 ns、388 mV [M]）、H01 Leduc 2025（430 mA、100 ns、480 mV、Iq 49 µA）。完整表在 `ARCH_MATRIX.md` §2，全部清單在 `literature.csv`（93 列）/`REFERENCES.md`。
**FoM 不可比的實例**：Seok DLDO 資料集（唯一實際開啟的資料，屬二手整理）46/58 列有邊沿時間，範圍 0.015–4000 ns、中位數 2 ns；同一顆 X. Wang CICC 2019：1 ns 邊沿 185 mV、10 ns 邊沿 88 mV。本次同一電路：0→100 mA 從 748 mV（0.1 ns）到 111 mV（1 µs），起點改 10 mA 時 1 µs 邊沿只剩 21 mV [X，`x2_edge_time.json`]。

### b.4 應用背景：HBM 與高速 SerDes（使用者追加，詳見 `APPLICATIONS.md`）
- **HBM**（12 篇＋13 補充來源）：HBM 介面專用 LDO 只找到首爾大學三篇（ISSCC 2025、JSSC 2026、CICC 2026，都是 hybrid/digital、靠 command/strobe 時序），標題指標是 droop/settling（<10 mV、400 ps、20 pF）。HBM rail 0.4–1.2 V，1.6 V 不是 HBM rail。學生晶片沒有 memory controller，hybrid 的主要好處用不到 [H]。
- **SerDes**（15 篇）：LDO 主要用在 PLL/VCO/clock，用寬頻 PSRR＋低雜訊換低 jitter（SD10 教學：PSRR 40 dB 撐到 10 MHz、50 nV/√Hz）[H，綜合摘要]。0.18 µm 例子都在 2.5 GHz 以下。
- **本次模擬（X5）**：7 級 ring（764 MHz、Kvdd 440 MHz/V）由 REF-A 供電，Vin 10 mV@1 MHz → 峰值 TIE 334 ps（無 LDO 915 ps，正弦擬合），手算 339/916 ps，差 ≤1.3% [X/D]；第 2 輪審查用另一顆振盪器在 3 個頻率獨立驗證（誤差 ≤2.9%）。REF-A 在 1 MHz 只擋 8.6 dB、10 MHz 放大 1.3 dB。
- **若以 PSRR/jitter 為主**：維持 PMOS pass＋feedforward（X6 顯示需 adaptive：完全抵消所需的過追蹤量隨負載變 15 倍，滿載 1 MHz 最好約 −13 dB [X/D]），或換 NMOS-pass 子類。第 3 輪 (c) 在**相同 Vout=1.0 V、相同 CL、相近 Iq** 下獨立比較（前一位審查者拿 1.0 V 的 NMOS 比 1.6 V 的 REF-A，不公平）：**10 MHz 好 13.5–20 dB（結構性：PMOS 的 Miller Cc 讓閘極跟著 Vout，開迴路 Vin→Vout 約 0 dB）**；1 MHz 只在輕載好（≤1 mA 12–21 dB、10 mA 11–13 dB、20 mA 5–10 dB）；**1 kHz 反而差 24–42 dB**；EA 也接 Vin 時 10 MHz 優勢仍在。另一審查者（第 3 輪 (a)）在 100 mA：1 ns undershoot 238–268 vs 719 mV、最低 Vin 1.73–1.76 V。Vout 上限：簡單 5T EA 時 10 mA 約 1.0 V，1.2 V 只能 ≤2 mA；用 charge pump 時閘極要 2.1–2.4 V，有 1.8 V 元件氧化層耐壓問題 [X，審查者]。

---

## c. 各架構電路分析（摘要；完整推導在 `ANALYSIS.md`）

### c.1 A1：兩級 Miller＋SF buffer（REF-A）
```
T0 = β·(gm1/G_ea)·A_SF·(gm_p/G_o)          p1 = G_ea·G_o / S
p2 ≈ (G2 + G_o)/CL  （G2 = A_SF·gm_p）       GBW ≈ β·gm1/Cc
z (RHP) = G2/Cc     p_b = (gm_b+gds_b+gds_cs)/C_pg
PSRR_LF = R_o·[gds_p + gm_p(1−α_pg)]/(1+T0) ≈ gds_p·R_o/(1+T0)（α_pg≈1）
```
- **手算 vs 模擬**（`s2_hand_vs_sim.py`）：零載 T0 53.2/53.0 dB、UGF 2.50/2.45 MHz、PM 66.4/66.4°；滿載 33.7/33.7 dB、1.61/1.60 MHz；全部誤差 <10%（最大是原始設計 PM +9.5%）。第 1 輪審查以 Middlebrook 雙注入法獨立量到差 <0.3%。p2 公式比 `.pz` 低 12%（p2 與 buffer 極點靠近）。
- **主導限制**：最輕載的 p2 ≈ I_min/(n·U_T·CL) → Cc ≳ 2.2·β·gm1·n·U_T·CL/I_min [D]。洩放 50 µA 時 PM 28°（100 pF、Cc=3 pF；Cc=5 pF 時 37.8°）；選 200 µA＋Cc 5 pF → 66°（Iq 131→287 µA）[X]。
- **滿載 pass 在 triode**：gm_p/gds_p = 1.33 → 迴路增益 53→33.7 dB、PSRR@1 kHz −55→−33 dB [X]。
- **失效情境**：(1) 洩放降到 50 µA → PM 28°（Cc=3 pF）／37.8°（Cc=5 pF）；(2) 1 ns 邊沿 0→100 mA → 742 mV；(3) SF-like 125 °C 零載 Vout +46 mV（4 mm pass 在 Vsg≈41 mV 仍漏 ~0.2 mA）——**第 2 輪審查指出可能是 PTM 假象**（|Vthp|+50 mV 即消失），待 PDK 確認。

### c.2 A2/A3/A6（FVF、SRE/adaptive、類比雙迴路）——推導為主
- FVF：DC 精度需第二迴路；X 節點掛整個 C_pg（slew = I_b/C_pg ≈ 6.3 V/µs）[D]。
- SRE（本次實作 class-B 電容耦合，X4）：小訊號幾乎不變（PM 差 ≤1°、PSRR 相同）；最佳參數 undershoot −8～15%；掃描最差 +48%（100 ns：236→348 mV）；第一版偏壓因 PTM PMOS 的 DIBL 靜態導通而整顆失效 [X]。
- 類比雙迴路：兩迴路頻寬要分開 5–10 倍以上，否則 doublet 長尾 [D/H]。

### c.3 B：類比主導 hybrid
- **兩迴路交互作用**：數位迴路看到的是「slice 電流 → pg 電壓」受控體。limit cycle 分界點 ≈ 1 ＋ 兩顆比較器 offset 之和（以片電流為單位）＋ 決策延遲 d（若不 blanking）；欠阻尼類比響應再推高。（offset 與欠阻尼：第 1 輪審查的行為模型 [X，審查者]；決策延遲 d：作者電路驗證 `s13` [X]，第 2 輪審查也以行為模型確認。）
- 電路級 [X]：窄窗（比值 0.49）20 mA 時 limit cycle 191–229 mV p-p；寬窗（1.23）無同步器 10/50 MHz 皆 0/31 負載點振盪；1 級同步器 11/31、**2 級同步器 26/31**；同步器＋shift register ÷(d+1) 時脈 0/31（`s13`）（初版接法錯誤：shift register 時脈晚 1 ns 使第 2 級同步器透明，量到的 11/31 其實是 d=1；第 2 輪 (c) 指出後更正）。
- **切換瞬間**：slice 閘極邊沿 1/30/300 ns → 正尖峰 82.6/71.4/34.5 mV [X]。
- **PSRR**：slice 導通是 Vin→Vout 的低阻抗開關，低頻差 8–14 dB；1–100 MHz 與 A 相同（≈0 dB）。
- **時脈與漣波**：本模型數位為理想，時脈饋通、kickback、電源彈跳**未模擬** [H]。
- **沒有 Verilog 能否實作**：可以。雙向 thermometer shift register = 每位元 1 DFF＋3 AND2＋1 OR3（本次 XSPICE 即閘級結構）＋2 比較器＋2 級同步器＋÷3 計數器。XSPICE 與閘級的差距：無 metastability、無 setup/hold 違規、比較器無 offset/kickback。
- **降級模式**：數位 reset 後公平 B 是 88.5 mA、PM 68° 的類比 LDO（審查者 [X]）。
- **卸載自造下陷（第 3 輪新發現）**：95→5 mA 後，類比 pass 被推到全關（pg=1.8 V、EA 飽和）時 slice 仍逐片移除，最後一片關掉的瞬間 Vout 掉到 1.07 V（比穩態低 ~530 mV）[X，`s20`]。前幾輪只看各平台最後 5 µs 所以沒看到。規則 [D]：類比迴路飽和時不要移除 slice（例如 DN 再 AND「Vout 已回到標稱附近」），或放慢 slice 關閉。
- **非同步 droop 路徑**（第 3 輪 (c) 行為模型＋電晶體級交叉檢查）：弛張振盪是真的（同步減片自造 0.13–0.6 V 下陷會重新觸發 droop），「卡死」重現不出來（9,088 次平台測試 0 次，可能是 XSPICE 事件排序假象）。**每次同步減片後遮蔽 droop 1 µs**（10 個時脈計數器）時，行為模型 18 種設定 0/64 失效、100 ns undershoot 145→59 mV——**若在電路級成立，B 的暫態會反超 A（127 mV）**；但只在行為模型驗證，且不能解決上一條的卸載下陷。

### c.4 C：數位主導
- 同步 DLDO 量化漣波 ≈ (I_u/2)/(CL·f_clk) [D]：8 片 12.2 mA、100 pF、10 MHz → 6 V（無法調節）；要把漣波壓到 ~50 mV，I_u=1 mA 需 f_clk ≈ 100 MHz。PTM 反相器 FO4 = 54–60 ps [X]。
- 本規格下找不到選 C 的強力理由（DLDO 的原始動機是 0.5 V 以下類比做不起來 [摘要 D01]）。

---

## d. 模擬結果與限制

### d.1 實驗清單（`bash sim/run_all.sh` 一鍵重跑，隔離副本測試約 2 分鐘＋新增項）
| 編號 | 主張 | 腳本 | 結果 [X] |
|---|---|---|---|
| X0 | 元件在 L=0.18/0.5/1 µm 的行為 | `s0_device_char.py` | gm/gds 隨 L 增加（NMOS 12→59→97）；Vth 對 L 不單調；PMOS L=0.18 在 Vsd=0.2 V 時 gm/gds=2.1 |
| X1 | 最輕載是最差 PM；CL 越大越難補償 | `s1_refA_sweep.py`（126 組） | 124/126 組最差點在零外部負載（另 2 組在 0.1 與 1 mA）；CL=1 nF、洩放 50 µA 時 Cc≤40 pF 都 ≤41° |
| — | 手算 vs 模擬 | `s2_hand_vs_sim.py` | 誤差 <10%（見 c.1） |
| — | REF-A 全特性 | `s3_refA_char.py` | Iq 287 µA；load reg 12.8 mV（0→100 mA）；dropout 94 mV@100 mA；line reg 4.6 mV/V；線性暫態（1.8↔1.98 V、1 µs、50 mA）±12 mV（100 pF） |
| X2 | 同電路 ΔV 隨邊沿/起點大幅變動 | `s4_exp_edge.py` | 748→21 mV |
| X3 | hybrid limit cycle、大步階、PSRR | `s5_exp_hybrid.py`、`s5b`、`s5c`、`s12`、`s13` | 見 c.3 |
| X4 | SRE 效果 | `s9_sre.py`、`s9b_sre_sweep.py` | −8～15% 到 +48% |
| X5 | 供電漣波→jitter | `s10_vco_supply.py` | 手算 vs 模擬 ~1% |
| X6 | feedforward PSRR 抵消的負載敏感度 | `s14_ff_psrr.py` | 所需過追蹤量隨負載變 15 倍（推導）；模擬最佳 gff 在 0/10/100 mA 為 0.06/0.1/≥1 mS（≥17 倍） |
| — | 規格敏感度、Rz 角落、板上電容 | `s8`、`s16`、`s17`、`s18` | 見 a、e、g |
| — | 資料集統計、補充查核、Rz 表/同條件 load reg、可重現補充、學習題 | `s7_dataset_stats.py`、`s11_misc_checks.py`、`s15_rz_loadreg.py`、`s19_repro_misc.py`、`learn.py` | 見各 json |
| — | 粗略角落 | `s6_corners.py` | 最差 PM 49.4°（FS-like 125 °C、1 nF/Cc 20 pF）；最大 1 µs undershoot 283 mV（SF-like 125 °C、1 nF） |

### d.2 限制（誠實清單）
1. **模型**：PTM 180nm、BSIM3v1（ngspice 以 version=3.1 解析）、lmin=lmax=0.18 µm（長通道是外插）、無 corner、無 mismatch；「角落」只是 Vth ±50 mV、Tox ±5%、溫度三點的擾動。LTspice 對 level 49 的實作可能不同，未驗證。
2. **理想元件**：Vref、偏壓電流源、負載（理想電流源）、比較器、數位邏輯（XSPICE）都是理想的；沒有 bandgap、沒有佈局寄生（第 2 輪審查加了 Cc 底板寄生才發現 Rz 振盪）。
3. **未模擬**：時脈饋通、基板耦合、ESD、封裝（除 s18 的簡化 bond wire）、熱、mismatch Monte Carlo、輸出雜訊。
4. **NMOS-pass 子類、B 的非同步 droop 路徑脆弱度**：只有審查者模擬，作者未重現。
5. **文獻**：92 篇僅摘要（X01 資料集除外）；數字未經全文核對。

---

## e. 反例與被推翻的想法

| # | 原本的想法 | 被誰、怎麼推翻 | 現在的版本 |
|---|---|---|---|
| 1 | 「B 比 A 差 2.5 倍、PSRR 差 19 dB」 | 第 1 輪 (a)：REF-B 類比 pass 只有 800 µm 是稻草人 | 公平 B 差 11–21%、PSRR 只在 ≤100 kHz 差 8–14 dB |
| 2 | 「1 nF 慢邊沿反而較差」 | 第 1 輪 (a)：加 Rz=10 kΩ 後 1 nF 全面較好 | 第 2 輪 (a)：Rz=10 kΩ 在角落振盪；穩健的小 Rz 下 1 nF **只在 1 ns 邊沿**占優 |
| 3 | 「首選 A 加 SRE」 | 作者自己的 X4：最好 −8～15%、最差 +48% | SRE 移出基準 |
| 4 | 「B/C 的 MHz PSRR 結構性吃虧」 | 第 2 輪 (b)：證據只到 100 kHz；審查者量 1 MHz A −6.7、B −4.1 dB | 撤回 |
| 5 | 「實作要加 2 級 DFF 同步器」 | 第 1 輪 (c) 行為模型：延遲 d 使分界點變 d+1 | 作者電路級確認（2 級同步器 26/31 → ÷3 後 0/31；初版量到的 11/31 因時脈接法錯誤只等於 d=1，第 2 輪 (c) 指出）：同步器要配 blanking |
| 6 | 「窗口 > 一片電流就不會 limit cycle」 | 第 1 輪 (c) | 還要加 offset 與決策延遲 |
| 7 | 「高溫輕載漏電是 A 的失效情境」 | 第 2 輪 (a)：可能是 PTM 的 PMOS Vth/DIBL 假象 | 降級為「待 PDK 確認」 |
| 8 | 「SF buffer 只能把 pg 拉到 ~1.65 V」 | 作者自己重跑 OP：實際 1.759 V | 已更正（失效原因是漏電而非擺幅） |
| 9 | 「HBM/SerDes 讓 PSRR 比暫態重要」 | 第 2 輪 (b)：HB05–07 的指標正是 droop/settling | 改為「兩者都重要；SerDes 時脈以 PSRR/雜訊為主 [H]」 |
| 10 | 「spur 差＝PSRR」 | 第 2 輪 (b)：只在 β≪1 成立；X5 在 1 MHz β=4.4 | 加條件，改用 TIE 比 |
| 11 | 「G1 量測方法學是主推缺口」 | 第 2 輪 (a)：監測 buffer 要 3–10 mA、板上電容讓 PM 掉到 18–30° | 降級；G6（LDO＋RO spur）為主 |
| 12 | 規格 1.8→1.6 V 視為給定 | 第 2 輪 (a) | 列為第一個要問教授的問題，提出 Vout 1.4 V 替代 |
| 13 | 「A vs B 差 11–21%」 | 第 3 輪 (a)：那是沒有同步器的理想 B；照報告自己的同步器規則 | 作者重現 `s20`：+41% undershoot、卸載回復慢約 16 倍 |
| 14 | 「首選 A、信心中偏低」 | 第 3 輪 (a)：把技術排序、首矽風險、教授意向混成一個信心 | 改為決策規則；信心分欄 |
| 15 | 「教授要 hybrid 就走 B」 | 第 3 輪 (a)：Leduc 依標題與 H02 摘要很可能是 C | 決策規則 ③：說明後以 B 或 H03 型類比雙迴路代替 |
| 16 | 「需要片上監測 buffer」 | 第 3 輪 (a)：直接 sense pad＋探棒看到 100–103% | 最小可行晶片不放 buffer |
| 17 | 「Vout 1.4 V 全面較好」 | 第 3 輪 (a) | 卸載過衝 206→404 mV（作者重現 `s21`） |
| 18 | 「B 不加 droop 路徑就穩定」 | 第 3 輪 (c)：卸載時 slice 在類比迴路飽和下被移除，自造 0.13–0.6 V 下陷 | 作者重現 `s20`：~530 mV；B 的設計規則新增「飽和時不減片」 |
| 19 | 「非同步 droop 路徑必然脆弱」 | 第 3 輪 (c)：遮蔽 1 µs 後行為模型穩定且 undershoot 59 mV | 改為「未遮蔽時必然振盪；遮蔽後可能可行，待電路級驗證」 |
| 20 | 「NMOS-pass 1–10 MHz 好 15–20 dB」 | 第 3 輪 (c)：前審查者比的是不同 Vout；同 Vout 時 10 MHz 好 13.5–20 dB、1 MHz 只在輕載、1 kHz 差 24–42 dB | b.4 與決策規則 ④ 改寫 |

完整紀錄：`REVIEW_LOG.md`；審查原文：`review/`。

---

## f. 研究缺口（詳見 `GAPS.md`；搜尋只到摘要層級，全部「未完整查證」）

| # | 缺口 | 判定 |
|---|---|---|
| G6 | 0.18 µm 類比 capless LDO＋片上 ring oscillator 當應用負載，實測 supply-induced spur/TIE 對漣波頻率曲線（應用層級的 PSRR 量測） | **保留（研究面的主推）**：PLL 論文常做但 regulator 屬 PLL；獨立 LDO＋RO 最接近的是 SD04（180 nm，只有模擬）。不能宣稱首創。**晶片上是否放 RO 依面積決定**（g.2 第 9 點）；最小可行晶片不含 |
| G1 | 片上可程式負載，系統化量 ΔV 對邊沿/起點/取出方式的依賴 | **保留但降級**（附帶量測設計，新穎性弱） |
| G2 | 類比主導 hybrid 的 dead band「洞」與同步器延遲 | **弱**（只在選 B 時有意義；H07/H08 可能已涵蓋） |
| G3 | 0.18 µm PSR feedforward | **刪除**（A01 已做） |
| G4 | SRE/FVF/SSF 快速暫態 | **刪除**（大量已有） |
| G5 | 高溫輕載漏電 | **刪除**（設計檢查項目，非研究缺口） |

---

## g. 下線與量測可行性

> 平台、PDK、面積上限與時程都未知（STATE.md「未解問題」；規格假設見 DECISIONS D-002）；除 [X] 外的面積、封裝數字都是 [H]，**必須用實際 PDK 重算**。

### g.1 面積粗估（首選 A，Imax 100 mA）
| 區塊 | 估計 |
|---|---|
| Pass PMOS W=4 mm, L=0.18 µm | 閘極 720 µm²；含金屬與接觸約 0.01–0.02 mm² [D/H] |
| CL=100 pF | MOS 電容（Cox≈8.2 fF/µm²）~0.012 mm²＋外框 [D] |
| CL=1 nF | MOS 電容 0.12–0.15 mm²；MIM（假設 1–2 fF/µm²）0.5–1 mm² [D/H] |
| 片上負載 NMOS | Vgs=1.8 V、Vds=1.6 V 時 0.72 mA/µm [X] → 100 mA 約 140 µm（留餘裕 200 µm） |
| Pads | 約 15–18 個（見 g.3），通常是學生晶片面積的主角 [H] |

### g.2 負載暫態要怎麼在晶片上量
1. **不能用外部負載**：bond wire ~1 nH 量級 [H] × 100 mA / 1 ns ≈ 100 mV 的 L·di/dt；外部負載邊沿通常 µs 級，會大幅美化 ΔV（同電路 1 µs 111 mV vs 1 ns 742 mV [X]）。
2. **片上負載產生器**：4–8 段二進位加權 NMOS，drain 接 Vout、source 接**獨立負載 GND pad**；閘極由 inverter chain 驅動，最後一級可切換強弱得到 ~1 ns / ~20 ns / ~200 ns 邊沿；外部函數產生器只提供觸發。段選擇可做不同起點電流（0、1、10 mA）。**熱**：100 mA×1.6 V = 160 mW，必須脈衝操作（例如 10 µs 導通、≥1 ms 週期）[D/H]。
3. **Vout 取出**：**直接 Vout sense pad＋高阻抗主動探棒即可**——第 3 輪審查模擬看到的是真值的 100–103%，而片上 buffer 要偏壓 ≥3 mA 才有約 97%（`review/round3_a_files/res/r3_4_direct_pad.json`，審查者 [X]）→ **最小可行晶片不放監測 buffer**。另加 VOUT_F（外接 DC 負載的備援）。
4. **量測板 Vout 腳不要放去耦電容**：1/10/100 nF（經 2 nH bond wire）讓最差 PM 掉到 28.7°/18.2°/19.9° [X，`s18`]。
5. 示波器/探棒頻寬 ≥500 MHz–1 GHz 才看得清 1 ns 邊沿 [H]；PSRR 用 bias-T 在 Vin 注入漣波，同時量 Vin 與 Vout。
6. 迴路增益無法直接在晶片上量；用負載步階振鈴推估 PM，或加測試模式 [H]。
7. **上電與 Vref**（第 3 輪審查，[X，審查者]）：21 種上電組合都沒有卡死；過衝隨 Vin 斜升變快而變大（1 µs 斜升 194 mV、10 µs 約 100 mV、1 ms 0.1 mV），讓 Vref 晚於 Vin 上電即可消除。**Vref 不能從 Vin 分壓**：那樣 PSRR 會量成 −1 dB；加 10 µF 濾波，1 kHz 也只量到 −49.7 dB（真值 −55.3 dB）。負載觸發/選擇腳要有片上 pull-down，避免浮接時變成 160 mW 連續負載。
8. **下線前沒有涵蓋的風險**：ESD 與 latch-up（pad 環由平台提供）、100 mA 的金屬電遷移與 IR、片上負載與 pass 的熱、上電順序；以及**只有 LTspice 時佈局/DRC/LVS/寄生抽取用什麼工具**——要問教授（h 節）。
9. （G6 的應用示範；晶片面積允許時放入，否則以 G1 的負載量測為主）LDO 輸出掛 7 級 ring oscillator（可關閉），經除頻器降到 <100 MHz 出 pad，Vin 注入 100 kHz–10 MHz 漣波，用頻譜儀/示波器量 spur/TIE；另一顆 RO 直接接 Vin 當對照。

### g.3 Pad 清單（草案）
**最小可行晶片（審查者建議，約 12 個 pad）**：VIN×2、GND(LDO)×2、GND(負載)×2、VOUT_SENSE、VOUT_F、LOAD_TRIG、LOAD_SEL×1–2、VREF_EXT。可選：IBIAS_EXT、ring oscillator 的 EN/OUT、更多負載段選擇。原草案（含監測 buffer 的 VOUT_MON、MON_VDD）約 15–18 個 [H]。備案 B 另需 CLK_IN、CODE_OUT、VL/VH 調整、數位 VDD/GND。

### g.4 時程（假設約兩學期到下線 [H]）
1. 用平台 PDK 重建 REF-A（含角落×溫度×寄生），重做 PM、PSRR、暫態（3 檔邊沿×3 起點）。
2. 決定是否加 PSR 增強或暫態增強，**只在所有角落都改善才保留**。
3. 片上負載與 monitor buffer 的設計與模擬（邊沿、熱、IR）。
4. 佈局（pass device、Vout/GND 金屬、Kelvin sense）、post-layout、DRC/LVS。
5. 量測板設計（Vout 腳不放電容、負載 GND 分離）。

---

## h. 要問教授的問題（依優先順序）

1. **規格**：Vin 從哪來、容差多少？Vout 一定要 1.6 V 嗎（1.4 V 時角落容差從 −4.7% 變 −13%，迴路增益 +15 dB）？Imax 要 10、50 還是 100 mA？主要指標是暫態、PSRR/jitter、Iq，還是完整量測流程？
2. **是否要求 hybrid？** 推薦 Leduc 2025 的用意是「要做 hybrid」還是「參考它的暫態做法/量測方式」？（決定首選/備案順序）
3. **下線平台**：TSRI？哪個製程？有無 3.3 V 厚氧元件、MIM 密度、標準元件庫？
4. **面積與 pad 上限**、封裝方式（COB/DIP/探針台）？
5. **時程**：下線與量測各在什麼時候？
6. **CL 預算**：100 pF 還是 1 nF？（1 nF 只對快邊沿有幫助，MOS 電容 0.12–0.15 mm²）
7. **負載暫態條件**：教授在意的邊沿時間與起點電流？（同電路從 21 mV 到 748 mV 都可能）
8. **Iq 預算**：可否接受 ~200 µA 洩放換輕載穩定？
9. **Vref/bandgap**：片上做還是外部給？（建議外部）
10. **量測資源**：示波器頻寬、主動探棒、可注入 Vin 漣波的設備、頻譜儀？
10b. **設計工具鏈**：只有 LTspice 的話，佈局、DRC/LVS、寄生抽取用什麼（平台提供的商用工具、或 Magic/KLayout＋Netgen 等開源工具）？PDK 有沒有 LTspice 可用的模型？
11. **應用動機**：要不要掛 HBM/SerDes？若要，可接受 Vout 降到 ~1.2 V 換 NMOS-pass 的高頻 PSRR 嗎？
12. 是否同意以 G6（LDO＋片上 ring oscillator 的 spur/TIE 量測）作為專題的應用示範？

---

## i. 還不確定的地方

1. **Leduc 2025 屬 B 或 C**：未確認（需全文或 Leduc 碩士論文 hybrid 章節）。
2. **A vs B 的排序**：兩者性能接近，排序依賴「驗證風險」與教授意向——這是判斷，不是數據。
3. **B 的非同步 droop 路徑脆弱**：只有審查者模擬，可能含 XSPICE 事件排序假象。
4. **NMOS-pass 子類**：兩位審查者各自模擬（同 Vout 1.0 V 下 10 MHz 好 13.5–20 dB、1 kHz 差 24–42 dB），作者未重現。
4b. **B 加遮蔽式 droop 路徑的效果**（59 mV）：只有行為模型；電路級未驗證。
5. **高溫輕載漏電失效**：可能是 PTM 假象。
6. **所有絕對數字**：PTM 模型＋理想偏壓＋無佈局；LTspice 結果可能不同。
7. **文獻數字**：除 X01 資料集外全部僅摘要；論文負載起點、CL 定義、邊沿時間多數未載明。
8. **研究缺口新穎性**：搜尋只到摘要層級、額度受限，G6 是否真的沒人做過未完整查證。
9. **feedforward PSR 的實作可行性**：X6 是理想 VCCS，不是電路。

---

## j. 參考文獻

完整 93 列（92 篇文獻＋1 個資料集；含 DOI/URL、全文狀態、類別）：**`REFERENCES.md`**（由 `literature.csv` 產生）。本報告直接引用的主要條目（全部「僅摘要」，DOI 為間接驗證或未驗證）：

- [H01] P. Leduc, X. Fu, Y. Zhou, “A 430-mA Capacitor Less Analog Assisted Hybrid LDO With Fast Transient Algorithm,” IEEE TCAS-I, vol. 72, pp. 3733–3743, 2025. <https://ieeexplore.ieee.org/document/10884555/>（DOI 未找到）
- [H04] P. Leduc, M.Sc. thesis, Lakehead University, 2024. <https://knowledgecommons.lakeheadu.ca/items/5f4ff6e9-7347-4087-a2a8-d81dc708904c>
- [A01] C.-J. Park, M. Onabajo, J. Silva-Martinez, “External Capacitor-Less Low Drop-Out Regulator With 25 dB Superior Power Supply Rejection in the 0.4–4 MHz Range,” IEEE JSSC, vol. 49, no. 2, pp. 486–501, 2014. DOI 10.1109/JSSC.2013.2289897
- [A02] H. Kim, S. S. Kwak, Y. S. Kim, “LDO Regulator Optimized on Power Efficiency and Load Transient Response with Voltage Damper and Body Loop Feedback,” IEEE ISCAS 2022, pp. 3571–3574. DOI 10.1109/ISCAS48785.2022.9937778
- [A05] Limpisawas, Wattanapanitch, IEEE Access, 2022. DOI 10.1109/ACCESS.2022.3185630
- [A06] S. Ni et al., Micromachines 13(10):1594, 2022. DOI 10.3390/mi13101594
- [A12] J. Torres et al., “Low Drop-Out Voltage Regulators: Capacitor-less Architecture Comparison,” IEEE CAS Magazine, 2014. DOI 10.1109/MCAS.2014.2314263（未驗證）
- [F03] Kao et al., IEEE Access, vol. 12, pp. 66539–66555, 2024. DOI 10.1109/ACCESS.2024.3398290
- [F04] Kao et al., IEEE Access, 2022. DOI 10.1109/ACCESS.2022.3157717
- [H11] Z. Jin et al., Electronics 12(15):3215, 2023. <https://www.mdpi.com/2079-9292/12/15/3215>
- [H06] M. Huang, Y. Lu, R. P. Martins, “Review of Analog-Assisted-Digital and Digital-Assisted-Analog Low Dropout Regulators,” IEEE TCAS-II, vol. 68, no. 1, pp. 24–29, 2021. <https://www.semanticscholar.org/paper/Review-of-Analog-Assisted-Digital-and-Low-Dropout-Huang-Lu/7d1e43a69eeb3176258eb15d5e6dbd78a0f952c7>
- [X01] M. Seok, Z. Wang, S. J. Kim, “Digital Low-Dropout Voltage Regulator (DLDO) Survey,” dataset. <https://github.com/mgseok/DLDO-survey>（commit 68e94cc；**本次實際開啟**）
- HBM：HB01–HB12（`lit_raw/agent5_hbm_notes.md`）；SerDes：SD01–SD15（`lit_raw/agent6_serdes_notes.md`）；PSR 技術：PS01–PS12（`lit_raw/agent7_psr_notes.md`）。
- 模型：PTM 180nm（ASU NIMO）經 SJTU-YONGFU-RESEARCH-GRP/spice_model_collections（CC BY 4.0），見 `sim/models/MODEL_ATTRIBUTION.md`。
