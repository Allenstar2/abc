# 最終檢查（REPORT.md 與 repo 一致性）

> 檢查者：最終檢查員（只用 repo 內容，未上網）。日期：2026-11-02。
> 範圍：`REPORT.md`（逐節 a–j）對 `sim/results/*.json`、`review/round*_files/res/*.json`（含 `round2_c_files/results/`）、`literature.csv`、`lit_raw/*`、`ext/DLDO-survey/DLDO survey.xlsx`（pandas 直接讀）、`sim/figs/*.png`、`sim/scripts/`、`sim/run_all.sh`；並交叉比對 `ANALYSIS.md`、`APPLICATIONS.md`、`REVIEW_LOG.md`、`LEARNING_ANSWERS.md`。
> 行號 L## 指 `REPORT.md` 目前版本的行號（其他檔案會寫檔名）。
> 執行的腳本：只執行 `s19_repro_misc.py`、`s21_vout14_overshoot.py`。執行前備份 `sim/results/`、`sim/netlists/`，執行後 `diff -rq` 確認內容**逐位相同**，再以備份還原時間戳；沒有修改任何既有檔案。

## 1. 逐項核對表

### 1.1 a 節（一頁結論）

| 位置 | 內容 | 來源 | 判定 | 建議修正 |
|---|---|---|---|---|
| a / L13 | SS-like 125 °C、100 mA 最低可調節 Vin 1.716 V | `s17_spec_alt.json` minVin_100mA_SS125 = 1.716 | 一致 | — |
| a / L13 | 只容許 −4.7% | (1.716−1.8)/1.8 = −4.67% | 一致 | — |
| a / L13 | Vout 1.4 V 容許 −13% | `s17` Vout1.4 SS125 = 1.56 V → −13.3% | 一致 | — |
| a / L13 | 滿載迴路增益 +15 dB | `s17` dc_db 48.6 vs 33.7 → +14.9 dB | 一致 | — |
| a / L13 | PSRR@1 kHz +13 dB | `s17` psrr_100mA −46.4 vs −33.3 → 13.1 dB | 一致 | — |
| a / L13 | 卸載過衝 206→404 mV（標 `s21`） | `s21_vout14_overshoot.json` 1 ns：206.4 / 404.0 mV；本次重跑相同 | 一致 | 同格的 −13%、+15 dB、+13 dB 來自 `s17`，可補標 |
| a / L15 | B 類比 pass ≈2.4 mm | `s12_fairB.json` Wa_um = 2400 | 一致 | — |
| a / L15 | 決策規則 ③：Leduc 依標題與 H02 摘要很可能是 C，仍未確認 | `literature.csv` H01/H02 notes；DECISIONS D-010 | 一致 | — |
| a / L15 | 決策規則 ④：5T EA 時 10 mA 上限約 1.0 V；1.2 V 只能 ≤2 mA | `round3_c_files/res/c1_headroom.json`：1.2 V 時 I_1% = 0.75/1.25/2.25 mA（W 1/2/4 mm）；1.0 V 時 21–40 mA 以上 | 一致（審查者） | — |
| a / L15 | NMOS-pass 1 kHz PSRR 差 24–42 dB | `c1_summary.json` 1 kHz Δ = +23.7～+42.3 dB | 一致 | — |
| a / L16 | 排除 C 的理由：「非同步路徑在 B 上就已經很脆弱（審查者模擬，作者未重現）」 | `round3_c_independent.md` §2：未遮蔽時振盪是結構性；每次減片後遮蔽 1 µs，行為模型 18 種設定 0/64 失效；REPORT 自己的 c.3 L88、e#19 已改寫 | 不一致（過時，與 c.3、e#19 衝突） | 改為「未遮蔽時必然振盪；遮蔽後行為模型可行，電路級未驗證」 |
| a / L18 | 照規則的 B（2 級同步器＋÷3）100 ns undershoot 180 vs 127 mV（+41%） | `s20_fairB_sync.json` 179.8 / 127.4 → +41.1% | 一致 | — |
| a / L18 | 回到 ±1%：2.3 vs 0.145 µs（約 16 倍） | `s20` 2.301 / 0.145 → 15.9 倍 | 一致 | — |
| a / L18 | 理想 B 差 21%、回復慢 5.5 倍 | `s20` 153.7/127.4 = 1.21；0.798/0.145 = 5.5 | 一致 | — |
| a / L19 | 1 ns、100 mA 步階、100 pF 時 undershoot >400 mV | `x2_edge_time.json` 0→100 mA 1 ns 742.2 mV；10→100 mA 451.9 mV | 一致 | — |
| a / L20 | B 卸載後約 530 mV 自造下陷 | `s20` 524.2 / 528.7 mV | 一致 | — |
| a / L20 | B 加遮蔽式 droop 路徑可能降到 59 mV（只有行為模型） | `round3_c_files/res/h2_summary_all.json` E_robust R2 nom 59.2 mV | 一致 | — |
| a / L20 | 「B 非同步 droop 路徑脆弱（審查者模擬，可能含 XSPICE 假象）」 | `round3_c_independent.md` L16、L273：振盪經行為模型＋不含 XSPICE 的電晶體級確認，**不是** XSPICE 假象；只有「卡死」疑似假象 | 不一致（過時） | 改為「未遮蔽時的弛張振盪已確認（第 3 輪 (c)，審查者）；只有『卡死』可能是 XSPICE 假象」 |
| a / L20 | 92 篇僅摘要 | `literature.csv` fulltext_status：92 僅摘要＋1 全文開放（X01） | 一致 | — |
| a / L22 | HBM rail 0.4–1.2 V；SerDes 時脈 rail 為 mW 級 | `APPLICATIONS.md` §2.1、§3.2；HB01–HB03、SD09/SD10 | 一致 | — |

### 1.2 b 節（架構概觀與比較矩陣）

| 位置 | 內容 | 來源 | 判定 | 建議修正 |
|---|---|---|---|---|
| b.2 / L38 | A 5→95 mA undershoot 499/127/27 mV（1 ns/100 ns/1 µs） | `s12_fairB.json` 498.9/127.5/27.4 | 一致 | — |
| b.2 / L38 | 理想 B 553/154/33 mV | `s12` 552.9/153.7/32.9 | 一致 | — |
| b.2 / L38 | 2 級同步器＋÷3：100 ns 180 mV | `s20` 179.8 | 一致 | — |
| b.2 / L39 | 卸載後回到 ±1%：A 0.145 µs；B 0.80 / 2.3 µs | `s20` 0.145 / 0.798 / 2.301 | 一致 | — |
| b.2 / L40 | 自造下陷 524–529 mV，Vout 掉到 1.07 V；A 0 mV | `s20`；`sim/figs/x7_B_release_dip.png`（看圖：最低約 1.07 V） | 一致 | — |
| b.2 / L40 | 第 3 輪 (c) 電晶體級交叉檢查 0.13–0.6 V | `c2_xcheck_spice.json` 285–611 mV；`c2b_partial.json` 133–165 mV | 一致 | — |
| b.2 / L41 | PSRR@1 kHz（70 mA）：A −38.2 dB | `s12` psrr_1kHz_70mA.A；`x3_hybrid.json` X3c | 一致 | — |
| b.2 / L41 | B −24.2 dB（碼 5，作者）～−30.1 dB（碼 3，審查者） | `s12` B_fair −24.2；`round2_a_files/res/r2_1_psrr_hf.json` code3 −30.1 | 一致 | — |
| b.2 / L41 | 資料集 8 列 @1 MHz：−5～−46 dB（中位 −27），多為 hybrid | `DLDO survey.xlsx` 直接讀：PSRR 8 列、頻率皆 1 MHz、−5…−46、中位 −27；5/8 為 hybrid | 一致 | — |
| b.2 / L42 | A 1 MHz −6.7 dB；10–100 MHz ≈0 dB | `x3` X3c 1 MHz −6.7、10 MHz +0.6；`r2_1` 100 MHz +0.2 | 一致 | — |
| b.2 / L42 | B 1 MHz −1.9～−4.1 dB；10–100 MHz 與 A 差 ≤0.6 dB（審查者） | `r2_1` code5 −1.9、code3 −4.1；10/100 MHz 差最大 0.5 dB | 一致 | — |
| b.2 / L43 | 同條件 load reg（20→95 mA）：A 6.1 mV、B 0.5 mV | `s15_rz_loadreg.json` 6.13 mV；`s12` plateaus 1.6006→1.6001 V | 一致 | — |
| b.2 / L45 | 8 DFF＋33 閘＋2 比較器 | `ANALYSIS.md` L161（32 閘＋1 NOR）、`ARCH_MATRIX.md` L64 | 一致 | — |
| b.3 / L49 | A01：PSR 優於 −56 dB 至 4 MHz @50 mA [M] | `literature.csv` A01 psrr、result_type M | 一致 | — |
| b.3 / L49 | A05：0–100 mA、CL 0–1 nF、Iq 14 µA | csv A05 | 一致 | — |
| b.3 / L49 | F03：0.1→100 mA、100 ns、<43.5 mV [M]、Vin 1.8–3.3 V | csv F03 | 一致 | — |
| b.3 / L49 | F04：0→100 mA、100 ns、388 mV [M] | csv F04 | 一致 | — |
| b.3 / L49 | H01：430 mA、100 ns、480 mV、Iq 49 µA | csv H01 | 一致 | — |
| b.3 / L49 | literature.csv 93 列 | csv shape (93, 31) | 一致 | — |
| b.3 / L50 | 資料集 46/58 列有邊沿時間，0.015–4000 ns，中位 2 ns | xlsx 直接讀：58 列、46 列、0.015、4000、2.0；`s7_dataset_stats.json` 相同 | 一致 | — |
| b.3 / L50 | X. Wang CICC 2019：1 ns 185 mV、10 ns 88 mV | xlsx 第 2、7 列 | 一致 | — |
| b.3 / L50 | 0→100 mA 748 mV（0.1 ns）→111 mV（1 µs）；起點 10 mA 時 1 µs 21 mV | `x2_edge_time.json` 748.2/111.0/21.4；圖 `x2_edge_time.png` 相符 | 一致 | — |
| b.4 / L53 | HBM 12 篇＋13 補充來源 | csv HB01–HB12；`lit_raw/agent5_hbm_notes.md` HBS1–HBS13 | 一致 | — |
| b.4 / L53 | 首爾大學三篇；<10 mV、400 ps、20 pF | csv HB05–HB07 | 一致 | — |
| b.4 / L54 | SerDes 15 篇；SD10：40 dB 至 10 MHz、50 nV/√Hz | csv SD01–SD15；SD10 psrr 與 notes | 一致 | — |
| b.4 / L55 | 7 級 ring 764 MHz、Kvdd 440 MHz/V | `x5_vco_supply.json` 764.2 / 439.9 | 一致 | — |
| b.4 / L55 | 峰值 TIE 334 ps（無 LDO 915 ps，正弦擬合）；手算 339/916 ps；差 ≤1.3% | `x5` sinefit 334.06 / 914.9；analytic 338.59 / 916.12 → −1.34% / −0.13% | 一致（−1.34% 剛好在四捨五入邊界） | — |
| b.4 / L55 | 第 2 輪 3 個頻率獨立驗證，誤差 ≤2.9% | `round2_c_files/results/a_cosim.json` CS5：−0.2%～−2.9% | 一致 | — |
| b.4 / L55 | REF-A 1 MHz 只擋 8.6 dB、10 MHz 放大 1.3 dB | `x5` analytic psrr −8.6 / +1.3 | 一致 | — |
| b.4 / L56 | X6：過追蹤量隨負載變 15 倍；滿載 1 MHz 最好約 −13 dB | `APPLICATIONS.md` §6.2 0.051→0.75（14.7 倍）；`x6_ff_psrr.json` gff 1 mS、100 mA、1 MHz −12.7 dB | 一致 | — |
| b.4 / L56 | NMOS-pass 同 Vout 1.0 V：10 MHz 好 13.5–20 dB | `c1_summary.json` 10 MHz Δ −13.5～−20.1 | 一致 | — |
| b.4 / L56 | 1 MHz：≤1 mA 12–21、10 mA 11–13、20 mA 5–10 dB | `c1_summary` 依負載分組：0/1 mA −11.9～−21.5、10 mA −11.2～−13.2、20 mA −5.4～−10.3 | 一致 | — |
| b.4 / L56 | 100 mA：1 ns undershoot 238–268 vs 719 mV | `round3_a_files/res/r3_7_nmos100.json` 237.6/247.0/267.8；`r3_7b_pmos1v.json` 719.2 | 一致 | — |
| b.4 / L56 | 最低 Vin 1.73–1.76 V | `r3_7b` 1.726 / 1.762 | 一致 | — |
| b.4 / L56 | charge pump 時「閘極要 2.1–2.4 V」 | `round3_c_independent.md` L115：閘極 2.10–2.28 V，使 V_GB 達 2.1–2.4 V | 不一致（輕微：把 V_GB 寫成閘極電壓） | 改「閘極 2.1–2.3 V（V_GB 達 2.4 V）」；`APPLICATIONS.md` L77 同 |

### 1.3 c 節（各架構電路分析）

| 位置 | 內容 | 來源 | 判定 | 建議修正 |
|---|---|---|---|---|
| c.1 / L69 | 零載 T0 53.2/53.0 dB、UGF 2.50/2.45 MHz、PM 66.4/66.4° | `s2_hand_vs_sim.json` | 一致 | — |
| c.1 / L69 | 滿載 33.7/33.7 dB、1.61/1.60 MHz | `s2` | 一致 | — |
| c.1 / L69 | 全部誤差 <10%，最大為原始設計 PM +9.5% | `s2` err_pct 最大 9.47% | 一致 | — |
| c.1 / L69 | Middlebrook 雙注入法差 <0.3% | `REVIEW_LOG.md` L34（52.99 dB/2.448 MHz/33.74 dB/1.598 MHz） | 一致 | — |
| c.1 / L69 | p2 公式比 `.pz` 低 12% | `REVIEW_LOG.md` L34：7.81 vs 8.89 MHz（−12.1%） | 一致 | — |
| c.1 / L70 | 洩放 50 µA：PM 28°（Cc 3 pF）／37.8°（Cc 5 pF） | `s1_refA_sweep.json`（100 mA、100 pF、Imin 50 µA）：28.1° / 37.8° | 一致 | — |
| c.1 / L70 | 200 µA＋Cc 5 pF → 66°；Iq 131→287 µA | `s1` 66.4°；`learn_answers.json` Q4 Iq 130.6 / 286.7 µA | 一致 | — |
| c.1 / L71 | gm_p/gds_p = 1.33；迴路增益 53→33.7 dB；PSRR@1 kHz −55→−33 dB | `s2` Ap 1.334；`s3_refA_char.json` psrr 0 mA −55.3、100 mA −33.3 | 一致 | — |
| c.1 / L72 | 1 ns 邊沿 0→100 mA → 742 mV | `x2`、`s3` 742.2 | 一致 | — |
| c.1 / L72 | SF-like 125 °C 零載 +46 mV；Vsg≈41 mV 時漏約 0.2 mA | `s6_corners.json` 1.6525−1.6061 = 46.4 mV；`s19` vpg 1.7594；`round1_a_files/res/r3b_hot.json` I_pass 206.6 µA | 一致 | — |
| c.1 / L72 | \|Vthp\|+50 mV 時失效即消失 | `round2_a_files/res/r2_7b_hot.json` dVthp +0.05 → 1.6139 V（+8 mV） | 一致 | — |
| c.2 / L75 | FVF slew = I_b/C_pg ≈ 6.3 V/µs | 50 µA / 7.87 pF（`s2` Cpg）= 6.35 V/µs | 一致 | — |
| c.2 / L76 | SRE：PM 差 ≤1°、PSRR 相同 | `x4_sre.json` PM 66.4→66.7°；psrr_50mA 完全相同 | 一致 | — |
| c.2 / L76 | 最佳參數 undershoot −8～15% | `x4b_sre_sweep.json`：最佳組 100 ns −7.9%、1 ns −11.5%；1 ns 最多 −15.8%（另一組） | 一致（範圍跨不同參數組；1 µs 只 −2%） | 可註明是不同參數組 |
| c.2 / L76 | 掃描最差 +48%（100 ns：236→348 mV） | `x4b` u100 最大 348 vs 235.5 mV | 一致 | — |
| c.3 / L81 | 窄窗（比值 0.49）20 mA limit cycle 191–229 mV p-p | `x3_hybrid.json` X3a narrow 190.8/216.0/229.4；6/12.2 = 0.49；圖 `x3a_limit_cycle.png` 窄窗 20 mA 段碼 0↔1 反覆 | 一致 | — |
| c.3 / L81 | 寬窗（1.23）無同步器 0/31；1 級 11/31；2 級 26/31；÷(d+1) 0/31 | `s13_hybrid_sync.json`；15/12.2 = 1.23 | 一致 | — |
| c.3 / L82 | slice 邊沿 1/30/300 ns → 尖峰 82.6/71.4/34.5 mV | `x3e_glitch_fo4.json` | 一致 | — |
| c.3 / L83 | 「低頻差 8–14 dB；**1–100 MHz 與 A 相同（≈0 dB）**」 | `r2_1_psrr_hf.json` 70 mA：1 kHz 差 8.1/14.0、100 kHz 差 3.9/8.0、**1 MHz 差 2.6/4.8 dB**、10–100 MHz 差 ≤0.5 dB；REPORT b.2 L42 自己就寫 1 MHz 有差；`round3_b_citation_check.md` #67 已指出；`REVIEW_LOG.md` L87 稱已修正 | 不一致 | 改「1 kHz 差 8–14 dB、100 kHz 4–8 dB、1 MHz 3–5 dB；10–100 MHz 差 ≤0.6 dB」 |
| c.3 / L86 | 數位 reset 後 88.5 mA、PM 68°（審查者） | `round1_a_files/res/r8_fallback.json` B2400：88.5 mA、68.3° | 一致 | — |
| c.3 / L87 | Vout 掉到 1.07 V（約 530 mV）；前幾輪只看最後 5 µs | `s20`；圖 x7 | 一致 | — |
| c.3 / L88 | 9,088 次平台測試 0 次卡死 | `round3_c_independent.md` L250 | 一致 | — |
| c.3 / L88 | 遮蔽 1 µs：18 種設定 0/64 失效、100 ns undershoot 145→59 mV | `h2_summary_all.json` E_robust R2：標稱＋17 種擾動共 18 種皆 0/64；nodroop 144.5 → 59.2 mV | 一致 | — |
| c.4 / L91 | 8 片 12.2 mA、100 pF、10 MHz → 6 V；I_u = 1 mA 需約 100 MHz（50 mV 漣波） | 代入 (I_u/2)/(CL·f)：6.1 V；0.5 mA/(100 pF×50 mV) = 100 MHz | 一致 | — |
| c.4 / L91 | PTM 反相器 FO4 54–60 ps | `x3e` tphl 60.3、tplh 53.9 ps | 一致 | — |

### 1.4 d 節（模擬結果與限制）

| 位置 | 內容 | 來源 | 判定 | 建議修正 |
|---|---|---|---|---|
| d.1 / L101 | X0：NMOS gm/gds 12→59→97；Vth 對 L 不單調；PMOS L=0.18 µm、Vsd=0.2 V 時 gm/gds 2.1 | `s0_device_char.json` 11.8/59.2/96.9；Vth 0.413/0.495/0.446；p_L0.18 2.1 | 一致 | — |
| d.1 / L102 | X1：126 組中 124 組最差點在零載（另 2 組在 0.1、1 mA）；1 nF、50 µA 時 Cc≤40 pF 都 ≤41° | `s1`：Counter {0: 124, 0.1: 1, 1.0: 1}；1 nF/50 µA 最大 41.0° | 一致 | — |
| d.1 / L104 | Iq 287 µA、load reg 12.8 mV、dropout 94 mV@100 mA、line reg 4.6 mV/V | `s3` dc 286.7 / 12.84 / 94.3 / 4.61 | 一致 | — |
| d.1 / L104 | 線性暫態（1.8↔1.98 V、1 µs、50 mA）±12 mV（100 pF） | `s3` line_tr：上 12.4 mV、下 13.1 mV；PWL 條件與腳本相符 | 不一致（輕微） | 改「+12/−13 mV」 |
| d.1 / L105 | X2：748→21 mV | `x2` | 一致 | — |
| d.1 / L107 | X4：−8～15% 到 +48% | `x4b` | 一致 | — |
| d.1 / L109 | X6：最佳 gff 0/10/100 mA 為 0.06/0.1/≥1 mS（≥17 倍） | `x6_ff_psrr.json`：1 kHz 最低點 −68.6@0.06、−68.5@0.1、−46.0@1.0；1/0.06 = 16.7 | 一致 | — |
| d.1 / L112 | 最差 PM 49.4°（FS-like 125 °C、1 nF/Cc 20 pF）；最大 1 µs undershoot 283 mV（SF-like 125 °C、1 nF） | `s6` 49.4（FS-like）、283.1（SF-like） | 一致 | — |
| d.1 表 | 實驗清單沒有列 `s20_fairB_sync.py`、`s21_vout14_overshoot.py`（a、b、e 節都引用） | `sim/run_all.sh` 有列 | 不一致（缺列） | d.1 加一列「s20/s21：照規則的 B、Vout 1.4 V 過衝」 |
| d.2 / L118 | NMOS-pass、非同步 droop 路徑只有審查者模擬，作者未重現 | REVIEW_LOG 第 3 輪 (c) 作者處理欄 | 一致（歸屬正確） | — |
| d.2 / L119 | 92 篇僅摘要（X01 除外） | csv | 一致 | — |

### 1.5 e 節（反例與被推翻的想法）

| 位置 | 內容 | 來源 | 判定 | 建議修正 |
|---|---|---|---|---|
| e#1 / L127 | 原想法「B 差 2.5 倍、PSRR 差 19 dB」 | `x3` X3b 313/127.5 = 2.46；X3c −18.8 vs −38.2 = 19.4 dB | 一致 | — |
| e#1 / L127 | 現在版本「公平 B 差 11–21%」 | `s12` 1 ns +10.8%、100 ns +20.6%、1 µs +20.1% | 一致 | — |
| e#1 / L127 | 現在版本「PSRR 只在 ≤100 kHz 差 8–14 dB」 | `r2_1`：8–14 dB 是 1 kHz 的數字；100 kHz 只差 3.9–8.0；1 MHz 仍差 2.6–4.8；`round3_b_citation_check.md` #10、#93 已指出 | 不一致 | 同 c.3 L83 |
| e#2 / L128 | Rz=10 kΩ 在角落振盪；穩健小 Rz 時 1 nF 只在 1 ns 邊沿占優 | `s16_rz_robust.json` −5.1°/−4.4°；Rz 3 kΩ 1 ns 468 vs 742 mV | 一致 | — |
| e#4 / L130 | 審查者量 1 MHz：A −6.7、B −4.1 dB | `r2_1` | 一致 | — |
| e#5 / L131 | 2 級同步器 26/31 → ÷3 後 0/31；初版 11/31 其實是 d=1 | `s13`；`round2_c_files/results/c1_beh.json` d1 11/31、d2 26/31 | 一致 | — |
| e#8 / L134 | SF buffer 實際把 pg 拉到 1.759 V | `s19` vpg_op 1.7594（本次重跑相同） | 一致 | — |
| e#11 / L137 | 監測 buffer 3–10 mA；板上電容 PM 18–30° | `r2_9_monitor.json`；`s18` 18.2–30.4° | 一致 | — |
| e#13 / L139 | +41% undershoot、卸載回復慢約 16 倍（作者重現 `s20`） | `s20` | 一致（作者確實重現） | — |
| e#16 / L142 | 直接 sense pad＋探棒看到 100–103% | `r3_4_direct_pad.json` ratio 1.000–1.033 | 一致 | — |
| e#17 / L143 | 卸載過衝 206→404 mV（作者重現 `s21`） | `s21`（本次重跑相同） | 一致 | — |
| e#18 / L144 | 0.13–0.6 V（第 3 輪 (c)）→ 作者重現約 530 mV | `c2`/`c2b`；`s20` | 一致 | — |
| e#20 / L146 | 同 Vout：10 MHz 好 13.5–20 dB、1 kHz 差 24–42 dB | `c1_summary` | 一致 | — |

### 1.6 f、g、h、i 節

| 位置 | 內容 | 來源 | 判定 | 建議修正 |
|---|---|---|---|---|
| f / L156 | G6 最接近 SD04（180 nm，只有模擬） | csv SD04 process 180 nm、result_type S | 一致 | — |
| g.1 / L172 | Pass W=4 mm、L=0.18 µm，閘極 720 µm² | 4000×0.18 = 720 µm² | 一致 | — |
| g.1 / L173 | Cox≈8.2 fF/µm² → 100 pF 約 0.012 mm² | `sim/models/180nm_bulk.pm` PMOS Tox 4.2 nm → 8.2 fF/µm²；100 pF/8.2 = 0.0122 mm² | 一致 | — |
| g.1 / L174 | 1 nF：MOS 0.12–0.15 mm²；MIM 0.5–1 mm² | 推導 [D/H] | 一致 | — |
| g.1 / L175 | 片上負載 0.72 mA/µm → 100 mA 約 140 µm | `s19` 0.721（本次重跑相同）；100/0.721 = 139 µm | 一致 | — |
| g.2 / L179 | 1 nH×100 mA/1 ns ≈ 100 mV；1 µs 111 mV vs 1 ns 742 mV | 推導；`x2` | 一致 | — |
| g.2 / L180 | 100 mA×1.6 V = 160 mW | 推導 | 一致 | — |
| g.2 / L181 | 直接 pad 看到 100–103%；片上 buffer 要 ≥3 mA 才約 97%，引 `r3_4_direct_pad.json` | `r3_4` 只有直接 pad 的數據；97% 出自 `round2_a_files/res/r2_9_monitor.json`（seen/true 0.80 ÷ DC 增益 0.826），經 `round3_a_counterexample.md` §6.1 表轉引 | 標記錯誤（來源檔） | 加註 `r2_9_monitor.json` |
| g.2 / L182 | 1/10/100 nF → 最差 PM 28.7°/18.2°/19.9° | `s18_offchip_cap.json` | 一致 | — |
| g.2 / L185 | 21 種上電組合都沒有卡死 | `r3_1_startup.json` 19 組＋`r3_1b_bias_late.json` 2 組；最終值皆正確 | 一致 | — |
| g.2 / L185 | 過衝 1 µs 斜升 194 mV、10 µs 約 100 mV、1 ms 0.1 mV | `r3_1` 193.7 / 97.5–102.3 / 0.1 | 一致 | — |
| g.2 / L185 | Vref 從 Vin 分壓 → PSRR −1 dB；加 10 µF，1 kHz −49.7 dB（真值 −55.3 dB） | `r3_5_vref_path.json` | 一致 | — |
| g.3 / L190 | 最小可行晶片約 12 個 pad | 列舉 11–12 個 | 一致 | — |
| g.4 / L195 | 時程第 3 步「片上負載與 **monitor buffer** 的設計與模擬」 | 與 g.2 第 3 點、g.3、e#16「最小可行晶片不放監測 buffer」矛盾；`REVIEW_LOG.md` L106 稱 g 節已改寫 | 不一致 | 刪去 monitor buffer（改「Vout sense pad／Kelvin 走線」） |
| h.1 / L203 | 1.4 V 時容差 −4.7%→−13%、迴路增益 +15 dB | `s17` | 一致 | — |
| h.6 / L208 | 1 nF 只對快邊沿有幫助；MOS 電容 0.12–0.15 mm² | e#2、g.1 | 一致 | — |
| h.7 / L209 | 同電路 21–748 mV | `x2` | 一致 | — |
| h.8 / L210 | 約 200 µA 洩放 | `s3` Iq 分解 | 一致 | — |
| h.11 / L214 | 「可接受 Vout 降到 **~1.2 V** 換 NMOS-pass 的高頻 PSRR 嗎？」 | a 決策規則 ④、b.4：5T EA 時 10 mA 上限約 1.0 V、1.2 V 只能 ≤2 mA（`c1_headroom.json`）；`round3_a_counterexample.md` 第 9 點已指出 | 不一致 | 改「~1.0 V（1.2 V 需 native NMOS、rail-to-rail EA 或 charge pump）」 |
| i.3 / L223 | 「B 的非同步 droop 路徑脆弱：只有審查者模擬，可能含 XSPICE 事件排序假象」 | `round3_c_independent.md`：振盪非 XSPICE 假象（電晶體級交叉確認），只有卡死疑似假象；遮蔽後可能可行 | 不一致（過時，與 c.3、e#19 衝突） | 同 a / L20 |
| i.4 / L224 | 「兩位審查者各自模擬」NMOS-pass | 實際有三份：第 2 輪 (a) `r2_10`、第 3 輪 (a) `r3_7`、第 3 輪 (c) `c1_*`；13.5–20/24–42 dB 只來自第 3 輪 (c) | 一致（措辭可更精確） | 可寫明來源輪次 |

### 1.7 j 節與引用

| 位置 | 內容 | 來源 | 判定 | 建議修正 |
|---|---|---|---|---|
| L5 | 93 列中 92 篇僅摘要，只有 X01 實際開啟；DOI 未經 doi.org 解析 | csv fulltext_status；DECISIONS D-009 | 一致 | — |
| j / L236 | 「本報告直接引用的主要條目（**全部「僅摘要」**）」 | 同一清單 L249 寫 X01「本次實際開啟」；csv X01 為「全文-開放」；`REVIEW_LOG.md` L89 稱這個矛盾已修 | 標記錯誤 | 改「除 X01 外全部僅摘要」 |
| j / L238 | H01 書目（TCAS-I vol. 72, pp. 3733–3743, 2025）、URL、DOI 未找到 | csv H01 | 一致 | — |
| j / L239 | H04 碩士論文 URL | csv H04 | 一致 | — |
| j / L240 | A01 書目＋DOI 10.1109/JSSC.2013.2289897 | csv A01（DOI 間接比對） | 一致 | — |
| j / L241 | A02 書目、pp. 3571–3574、DOI | csv A02 | 一致 | — |
| j / L242–243 | A05、A06 DOI | csv | 一致 | — |
| j / L244 | A12 DOI（未驗證） | csv A12 | 一致 | — |
| j / L245–246 | F03（vol. 12, pp. 66539–66555）、F04 DOI | csv | 一致 | — |
| j / L247 | H11 URL | csv | 一致 | — |
| j / L248 | H06 書目（TCAS-II 68(1) 24–29, 2021）＋URL | csv | 一致 | — |
| j / L249 | X01 URL、commit 68e94cc、實際開啟 | csv X01 | 一致 | — |
| j / L250 | HB01–HB12、SD01–SD15、PS01–PS12 | csv 三組 id 皆齊全 | 一致 | — |
| 全文 [id] | REPORT 26 個 id、APPLICATIONS 35 個、ANALYSIS 7 個 | 全部存在於 `literature.csv` | 一致 | — |
| 審查者 vs 作者歸屬 | b.2 碼 3 −30.1、b.4 NMOS-pass、c.3 降級模式、g.2 第 3 和 7 點都標審查者；e#13/#17/#18 的「作者重現」都有 `s20`/`s21` 存檔 | — | 一致（沒有把審查者模擬寫成作者重現） | — |
| 未驗證寫成已驗證 | 遮蔽式 droop 59 mV（c.3、i.4b）都標「只有行為模型」；Leduc 標未確認 | — | 一致 | — |
| L3 | 版本「第 2 輪審查後初稿」 | 內容已含第 3 輪 (a)(b)(c) | 標記錯誤（輕微） | 改「第 3 輪審查後」 |

### 1.8 圖

| 位置 | 內容 | 來源 | 判定 | 建議修正 |
|---|---|---|---|---|
| REPORT L40、ANALYSIS L290 | `sim/figs/x7_B_release_dip.png` | 檔案存在。看圖：95→5 mA 後 Vout 衝到約 1.79 V；碼每約 0.3 µs 減 1（10 MHz、÷3）；約 2.05 µs 最後一片關掉時 Vout 掉到約 1.07 V，約 2.4 µs 回到 1.60 V | 一致（與「Vout 掉到 1.07 V」「先衝到 ~1.79 V」「每 3 個時脈移除一片」「回復 2.3 µs」相符） | — |
| REPORT b.3（引 json） | `x2_edge_time.png` | 看圖：100 pF、0 mA 起點 0.1 ns 約 748 mV、1 µs 約 111 mV；10 mA 起點 1 µs 約 21 mV；1 nF 曲線較平 | 一致 | — |
| REPORT c.3 L81 | `x3a_limit_cycle.png` | 看圖：窄窗 20 mA 段碼 0↔1 反覆、Vout 擺幅 >200 mV；45/70/95 mA 與寬窗都穩定 | 一致（y 軸下緣 1.45 V 截斷，無法從圖讀 p-p 精確值） | — |
| REPORT/ANALYSIS/APPLICATIONS | 以檔名引用的圖只有 x7 一張 | `sim/figs/` 11 張全部存在 | 一致 | — |

### 1.9 腳本

| 位置 | 內容 | 來源 | 判定 | 建議修正 |
|---|---|---|---|---|
| 全文 | REPORT 引用的腳本（s0–s21、s5b、s5c、s9b、learn.py 等 26 個） | 全部在 `sim/scripts/`，全部列於 `sim/run_all.sh` | 一致 | — |
| g.2 / L181 | 引用路徑 `review/round3_a_files/res/r3_4_direct_pad.json` | 檔案存在 | 一致 | 見上方來源檔註記 |
| 實際執行 | `python3 s19_repro_misc.py` → nmos_load 0.721 mA/µm；SF-like 125 °C：Vout 1.6525、pg 1.7594、ea 1.6429 | 與 `s19_repro_misc.json`（逐位相同）及 REPORT g.1、e#8、c.1 一致 | 一致 | — |
| 實際執行 | `python3 s21_vout14_overshoot.py` → 1.6 V：742.2/206.4、449.6/206.4、235.5/205.6；1.4 V：743.0/404.0、453.3/403.8、240.7/318.4 mV | 與 `s21_vout14_overshoot.json`（逐位相同）及 REPORT a、e#17 一致 | 一致 | — |

### 1.10 內部一致（跨節、跨檔）

| 位置 | 內容 | 來源 | 判定 | 建議修正 |
|---|---|---|---|---|
| REPORT a、b.2、c.3、e#13、e#18 | 180/127 mV、2.3/0.145 µs、524–529 mV、1.07 V | 各節相同；ANALYSIS L289–290、LEARNING_ANSWERS L89 相同 | 一致 | — |
| REPORT a L18 vs c.3 L83 | a 寫「PSRR 只在 ≤1 MHz 有限差距」，c.3 寫「1–100 MHz 與 A 相同」 | 見上 | 不一致 | 依 c.3 修正 |
| REPORT a L15/b.4 vs h.11 | Vout 上限 ~1.0 V vs ~1.2 V | 見上 | 不一致 | 依 h.11 修正 |
| REPORT g.2/g.3/e#16 vs g.4 | 不放 buffer vs 設計 monitor buffer | 見上 | 不一致 | 依 g.4 修正 |
| REPORT c.3 L88/e#19 vs a L16/L20、i.3 | 非同步 droop 路徑的狀態 | 見上 | 不一致 | 依 a/i.3 修正 |
| REVIEW_LOG L87、L89、L106 vs REPORT | REVIEW_LOG 稱「PSRR 頻段」「全部僅摘要」「g 節拿掉 buffer」已修正，REPORT 仍有舊文字（c.3 L83、e#1 L127、j L236、g.4 L195） | `REVIEW_LOG.md` 第 3 輪 (b)(a) | 不一致 | 修 REPORT，使 REVIEW_LOG 屬實 |
| ANALYSIS L66 | 「1 nF＋Rz=10 kΩ……**全面優於** 100 pF 的 REF-A」沒加刪除線，也沒註明第 2 輪已推翻 | ANALYSIS L221–234；REPORT e#2 | 不一致（ANALYSIS 過時） | 加刪除線或「第 2 輪推翻，見附錄」 |
| ANALYSIS L11–16、L68、L78、L80、L155–156、L275 | gm_p 347/gds_p 260 mS、C_gg 5.5–7.9 pF、206 mV、2.2/0.32 µs、−56.7 dB、414 MHz、−38.2/−18.8、1.5975 V、−7%/−16% | `s2`、`s3`、`s11`、`x3`、`x3d`、`s15`、`s17` | 一致 | — |
| ANALYSIS L265 | SF-like 125 °C：B800 +9、公平 B +28、A +46、A 洩放 300 µA +26 mV | `r3b_hot.json`、`r7_bleed_bias.json`（300 µA → 1.6324 V） | 一致 | — |
| APPLICATIONS L46、L60–61、L66、L97、L102–105 | 925/335 ps = 8.8 dB；+1.0%/−0.1%、−1.0%/−1.3%；−0.2～−2.9%；0.051/0.074/0.75；X6 表 | `x5`、`a_cosim`、`x6` | 一致 | — |
| APPLICATIONS L77 | charge pump「閘極 2.1–2.4 V」 | 同 b.4 | 不一致（輕微） | 同 b.4 |
| APPLICATIONS L71 | 標題「agent7 PSR 技術待補」，但 §6 已補上 agent7 | — | 標記錯誤（輕微） | 刪去「待補」 |
| LEARNING_ANSWERS L27、L33、L69、L87、L89、L91、L94 | 37.8/66.4/78.1°、131/287/589 µA、742/627/452 mV、51%、1.716 V/−4.7%、530 mV、26/31→0/31、8–15%/+48% | `learn_answers.json`、`x2`、`s17`、`s20`、`s13`、`x4b` | 一致 | — |
| LEARNING_ANSWERS L83、L96 | 「Vout 經片上 buffer 取出」「片上監測 buffer」 | REPORT g.2 第 3 點、e#16 已決定不放 | 不一致 | 改為直接 sense pad＋主動探棒 |
| GAPS.md G1、CONCLUSION_DRAFT L9/L12/L18 | 仍有監測 buffer、「1–100 MHz 差 ≤0.6 dB」、「Vout ≤ ~1.2 V」、「14–18 dB」 | 都是舊版（REPORT 已更新） | 不一致（低優先，屬草稿/附件） | 同步更新，或在檔頭註明「已被 REPORT 取代」 |
| 章節 | a 一頁結論、b 架構概觀＋比較矩陣、c 各架構電路分析、d 模擬結果與限制、e 反例、f 缺口、g 下線與量測（g.2 含負載暫態如何在晶片上量）、h 問教授、i 不確定、j 參考文獻 | REPORT 標題 L9–L234 | 一致（a–j 齊全） | h 節編號「10b」可改成連續編號 |

## 2. 統計

| 判定 | 列數 |
|---|---|
| 一致 | 143 |
| 不一致 | 19（其中 6 項列為必須修正；其餘為輕微或屬附件／草稿） |
| 標記錯誤 | 4 |
| 缺檔 | 0 |
| **合計** | **166** |

- 抽查的數字超過 120 個（a、b、c 節逐一核對，d–h 節大部分核對）；**數字層級幾乎沒有抄寫錯誤**。主要問題是**舊文字沒跟著第 3 輪修正一起改**：REVIEW_LOG 宣稱已修正，但 REPORT 還留著舊版本。
- 圖：x7、x2、x3a 三張看圖後與文字一致；被引用的圖都存在。
- 腳本：被引用的都存在且列在 `run_all.sh`；`s19`、`s21` 重跑後輸出與 json 逐位相同。
- 引用：所有 [id] 都在 `literature.csv`；DOI/URL 一致；沒有把審查者模擬寫成作者重現，也沒有把未驗證寫成已驗證。唯一的標記問題是 j 節的「全部僅摘要」。

## 3. 必須修正（REPORT.md）

1. **c.3 L83 PSRR 頻段**：「1–100 MHz 與 A 相同（≈0 dB）」與 b.2 L42 及 `r2_1_psrr_hf.json` 矛盾（1 MHz 差 2.6–4.8 dB）。改「1 kHz 差 8–14 dB、100 kHz 4–8 dB、1 MHz 3–5 dB；10–100 MHz 差 ≤0.6 dB」。
2. **e#1 L127**：「PSRR 只在 ≤100 kHz 差 8–14 dB」，改法同上（8–14 dB 是 1 kHz 的數字；100 kHz 只差 4–8 dB）。
3. **h.11 L214**：「Vout 降到 ~1.2 V」與 a 決策規則 ④、b.4 矛盾（5T EA 時 10 mA 上限約 1.0 V，1.2 V 只能 ≤2 mA）。改 ~1.0 V。
4. **g.4 L195**：時程仍有「monitor buffer 的設計與模擬」，與 g.2 第 3 點、g.3、e#16「最小可行晶片不放監測 buffer」矛盾。刪去。
5. **a L16、a L20、i.3 L223**：「非同步 droop 路徑脆弱（可能含 XSPICE 假象）」已過時。第 3 輪 (c) 用不含 XSPICE 的電晶體級確認振盪是真的，只有「卡死」疑似假象；遮蔽 1 µs 後在行為模型裡可行。要與 c.3 L88、e#19 一致。
6. **j L236**：「全部『僅摘要』」與同一清單中 X01「本次實際開啟」矛盾。改「除 X01 外全部僅摘要」。

### 建議修正（不影響結論）
- b.4 L56、APPLICATIONS L77：閘極 2.10–2.28 V，2.4 V 是 V_GB。
- d.1 L104：線性暫態 ±12 mV → +12/−13 mV；d.1 表補列 `s20`、`s21`。
- g.2 L181：97% 的來源檔是 `r2_9_monitor.json`，不是 `r3_4_direct_pad.json`。
- L3 版本說明改為「第 3 輪審查後」；a L13 的 −13%/+15 dB/+13 dB 補標 `s17`。
- ANALYSIS L66「全面優於」加刪除線；LEARNING_ANSWERS L83、L96 的監測 buffer；APPLICATIONS L71「待補」；GAPS G1 與 CONCLUSION_DRAFT 同步或註明已被取代。
