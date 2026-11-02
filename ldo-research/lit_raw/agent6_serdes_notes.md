# agent6 筆記：LDO／supply regulation 在 SerDes／wireline 裡的用途（應用背景）

對應 CSV：`agent6_serdes.csv`（SD01–SD15）。搜尋日期 2026-11-02。WebSearch 用了 42 次（上限 45）。

## 先讀：這批資料的限制

1. **全文一篇都沒開。** 學術網站被本 session 的網路政策封鎖，依指示沒有嘗試 WebFetch/curl。書目與數字都來自 WebSearch 回傳的摘錄。這些摘錄本身經過整理，可能有誤。
2. **DOI 都沒經 doi.org 驗證。** 只填了摘錄中明確出現的 DOI（SD01、SD05、SD07、SD08、SD10），其餘留空。
3. **只讀到摘要，所以不推論電路細節。** 例如 SD03 的 regulator 是什麼拓樸、SD02 的外接 LDO 規格，都沒讀到。
4. **篇數**：2014 至今 13 篇（SD01–SD13）；另有 2 篇 2014 前的 0.18 µm 背景文獻（SD14、SD15）。收錄後兩篇是因為任務要求找 0.18 µm 或較舊製程的例子，而 2014 後符合的只找到 SD04（僅模擬）和 SD06（數字未讀到）。
5. **CSV 外的來源**用以下代號引用（不是同儕審查論文，或早於 2014）：
   - [P1] US 9973176 / US 10727818 "Circuits for digital and analog controlled oscillators"（專利）
   - [P2] US 9746864 "Fast transient low drop-out voltage regulator for a voltage-mode driver"（專利）
   - [P3] US 9853642 "Data-dependent current compensation in a voltage-mode driver"（專利）
   - [P4] US 12326747 "Dual-mode low dropout regulator with fast transient switching between modes"（專利）
   - [P5] US 8957735 "Phase-locked loop (PLL) circuit and communication apparatus"（專利）
   - [B1] Wu, Mayaram, Moon, ring oscillator 的 on-chip calibration，IEEE JSSC 2007（2014 前）
   - [B2] "A 1.25–5 GHz Clock Generator With High-Bandwidth Supply-Rejection Using a Regulated-Replica Regulator in 45-nm CMOS"（IBM；專利引用寫 JSSC vol. 44, no. 11，年份 2008/2009 不一致，作者欄在各 IBM 鏡像頁也不一致；2014 前）
   - [B3] "Studies on sensitivity of clock and data recovery circuits to power supply noise"（Maltepe 大學典藏；搜尋摘要年份寫 2009 和 2011 兩種，2014 前，模擬）
   - [B4] Sun et al.（北航），Microelectronics vol. 41 no. 4，2010：0.35 µm CP-PLL 的 CP/VCO 雙軌 regulator（2014 前）
   - [B5] Gui & Green, IEEE TCAS-I vol. 60, 2013, pp. 1753–1763（2014 前）
   - [B6] 0.13 µm PLL，Journal of Semiconductors（jos.ac.cn 舊版 PDF 10030901，年份未確認，推測 2014 前）
   - [B7] Chang & Horowitz 的 replica-compensated LDO（designers-guide.org 論壇附件 PDF，出處年份未確認）
   - [O1] Analog Devices, Analog Dialogue "Power Management Design for PLLs"（應用文章）
   - [O2] Analog Devices CN0147 circuit note（ADF4350 + 不同雜訊 LDO）
   - [O3] UCLA eScholarship 101492q7（SD02 同設計的學位論文摘要）

---

## §1 SerDes 裡 LDO 的典型位置與需求概觀

**(a) PLL／VCO／ring oscillator 供電：最常見、也最在意 PSRR 和雜訊的位置。**
- Ring oscillator 對 supply 很敏感，supply noise 會讓含 ring VCO 的 PLL 相位雜訊變差；用 LDO 供電可改善，但 LDO 需要電容來壓住高頻雜訊。[P5]
- Full-swing ring VCO 的頻率大致正比於 supply 電壓。"supply-regulated tuning" 就是利用這點，把 regulator 輸出直接當 VCO 的調頻控制（0.18 µm、1.8 V 實例）。[SD14]
- 到 >100 Gb/s SerDes，ring oscillator 仍被用來產生多相時脈。演講摘要指出它在 10 GHz 以上 supply sensitivity 很高，因此用 type-III supply-regulated 架構。期刊版在 50 mVpp 漣波下把 spur 壓在 −54 dBc 以下。[SD03]
- 一顆 5 GHz 振盪器的 Kvcc 可達約 5.5 GHz/V，所以 regulator 的 PSRR 要很高，而且 regulator 自身的 thermal 與 flicker noise 會直接變成 jitter。[P1]
- 教學文把需求量化：替 5-GHz LC VCO 供電的 LDO，PSRR 40 dB 要撐到 10 MHz，輸出雜訊 50 nV/√Hz @1 MHz，相位雜訊惡化不超過 1 dB，功耗 overhead ≤1 mW。[SD10]
- 也有不用 PMOS LDO、改用 source-follower regulator 的 PLL（3.12 mW @1 V，65 nm）。[SD08]

**(b) Clock distribution／CDR。**
- 45 nm 的 link 收端時脈產生器（DLL + phase rotator）用 regulated-replica regulator：80 pF 去耦下 PSR >22 dB 可到 1 GHz，最大 supply sensitivity 4.5 ps/100 mV。[B2]
- 一篇模擬研究指出：CDR 不加 LDO 只能容忍約 20 mV/10 MHz 的 supply noise，加 LDO 後可容忍 200 mV/10 MHz。[B3]
- 也有不用 LDO、改用 adaptive filter 抵銷 clock distribution 的 supply-noise-induced jitter 的作法（LPDDR5，記憶體介面）。[SD13]

**(c) TX driver／serializer。**
- 112 Gb/s PAM4 TX：SST DAC 依標稱擺幅設計，擺幅可程式化交給外接 LDO 供應的 VDD；摘錄轉述文中說一般系統的 TX 各段常用 LDO。[SD02] 同設計的學位論文用分開的 LSB／MSB LDO 微調 PAM4 非線性。[O3]
- 粒子物理用 10.24 Gb/s TX 晶片內放 capless LDO 給關鍵區塊與 PLL，目的是在吵雜的晶片電源下仍正常工作；摘要轉述 PSRR −50 dB（<1 MHz）。[SD11]
- 專利指出：voltage-mode driver 的擺幅由 regulator 設定，supply ripple 會影響 jitter，所以 regulator 要快 [P2]；driver 從 regulator 抽的資料相依電流會惡化 deterministic jitter [P3]；pre-driver 需要比 core 高的供電，所以常用分開的 LDO，而共用 LDO 在高資料率下有頻寬和 IR drop 問題 [P4]。

**(d) RX front-end（CTLE／slicer）。**
- 只找到一篇：224 Gb/s/lane 單端 PAM-4 front-end（130 nm SiGe）的 TX 與 RX 都用 pseudo-differential 結構加 dual-loop regulator，以取得高 PSR。[SD12]
- CMOS RX 的 CTLE／slicer 用 LDO 的例子，本次在摘要層級沒找到（見 §5）。

**(e) 整體需求的共同點。**
- LDO 只能濾掉其調節頻寬內的雜訊；同 rail 上快速切換電路的雜訊若高於此頻寬，就會打到 VCO（第一次搜尋中某專利摘錄如此描述，專利編號未能確定對應，視為 [H] 等級）。頻寬以上要靠電容 [P5]；PSRR 目標決定 op-amp 頻寬 [SD10]。
- regulator 若放在 PLL 迴路內（supply-regulated PLL），其頻寬要遠高於 PLL 閉迴路頻寬。[B7] 迴路內的 regulator 漣波也會變成 spur。[SD09]
- LDO 的雜訊對 PLL 的貢獻是加成的（RSS），而且只在 loop bandwidth 外才明顯，loop bandwidth 內會被 PLL 壓下來。[O1] 實例：同一顆 PLL/VCO，150 nV/√Hz 的 LDO 比 25 nV/√Hz 的 LDO 讓相位雜訊明顯變差。[O2]
- 綜合以上：SerDes 裡的 LDO 主要不是拿來應付大負載暫態，而是用 **PSRR（尤其 MHz 以上）+ 低雜訊 + 小功耗** 換低 jitter。[H]

---

## §2 每篇重點

### SD01 Yeh, Hsieh, Liu — ISSCC 2016，3.2 GHz DPLL with background supply-noise cancellation（Crit）
- 動機：decap 佔面積，LDO 要額外功耗與面積，所以改走 cancellation 路線。
- 架構（摘錄層級）：digital LDO + supply-noise cancellation controller；可容忍 240 mVpp supply noise。
- 同指導教授的台大碩論在 50 mVpp、10 kHz 下 pp jitter 41.87→29.11 ps，但不能確認是同一晶片。
- 對學生：說明 LDO 在時脈應用的「代價」論點；也顯示數位 LDO 單獨用不夠，還要加 cancellation。

### SD02 Forghani, Zhao, Khanna, Razavi — VLSI 2023，112 Gb/s 58 mW PAM4 TX（App）
- 28 nm；RLM 96%；VDD 提高 150 mV 使 RLM 達 99%，多耗 14 mW [M]。
- 擺幅可程式化交給外接 LDO 供應的 VDD。
- 對學生：可引用為「LDO 在 TX 的角色＝設定擺幅與線性度」的實例。但 LDO 是外接的，規格不明，不能當電路參考。

### SD03 Khalil, Hanumolu, et al. — JSSC 2026（in press），6.8–14 GHz ring sampling-PLL（App）
- 22 nm FinFET；69.3 fs（10 kHz–100 MHz）；8 相輸出；目標是 >100 Gb/s serial link。
- supply regulation 讓 noise immunity 改善 31.4 dB；50 mVpp 正弦漣波下最差 spur < −54 dBc [M]。
- 同組演講摘要：Intel 16 原型、supply noise rejection >30 dB、type-III supply-regulated 架構（可能不是同一晶片）。
- 對學生：是目前最強的「SerDes 時脈需要 supply regulation」證據；「注入正弦漣波→量 spur」的量測法可直接借用。

### SD04 Jyväskylä 碩士論文 2026 — 給 supply-tuned PLL 的 regulator（A，180 nm，僅模擬）
- PMOS pass、兩級 Miller 補償 EA、bandgap、startup；負載是 5 級 RO。
- 輸出雜訊約 24.8 µVrms（1 kHz–1 MHz）；local regulation 讓 RMS period jitter 降約 64–71% [S]。
- 對學生：和「0.18 µm 類比 LDO + 片上 RO」幾乎同題，可作為最直接的對照組。差別是它沒下線，學生有量測就有區隔。

### SD05 Tripathi, et al. — IEEE Access 2019，CMOS buffer 的 PSIJ 模型（Mx）
- 以 Thomas algorithm 建 supply noise 與 PSIJ 的半解析關係，涵蓋等尺寸 inverter chain 與 tapered buffer [S]。
- 對學生：可用來把 LDO 輸出漣波換算成 RO 或 clock buffer 的 jitter（OA 期刊，最容易拿到全文）。

### SD06 Wang, Bai, Diao, Lin — 2017，CML RO 的 open-loop supply 補償（Crit，180 nm）
- 用具負 supply sensitivity 的 bias 電流，抵銷 CML VCO 本身的正 sensitivity；180 nm 原型。
- 刊物名與量測數字未讀到。
- 對學生：同製程的「不加 LDO」替代方案，可在報告的 related work 中當對照。

### SD07 D. Kim, S. Cho — VLSI 2017，wideband noise suppression loop PLL（Crit）
- 摘錄指出：既有 regulate/calibrate 法會犧牲 oscillator headroom；本作改在 RO 外加寬頻回授，無 headroom 損失、不需 calibration。
- 65 nm、3.2 GHz、2.73 mW，loop BW 附近約 30 dB spur suppression [M]。
- 對學生：這是「headroom 不夠所以不用 LDO」最直接的論據。但在 0.18 µm、1.8 V 下這個限制較弱（見 §4）。

### SD08 Jo, H. J. Kim, S. Cho — TVLSI 2018，gate-boosted source-follower regulator PLL（A）
- 65 nm、1 V、3.12 mW；50 mVpp supply noise（近 loop BW）下 spur < −33 dBc [M]。
- 用 gate-voltage boosting 降低 SF regulator 的壓降，另加 body-controlled noise cancellation 處理殘餘雜訊。
- 對學生：PLL 專用 regulator 常不是 PMOS LDO，而是 NMOS source follower。這可以當報告中「為何選 PMOS pass」的討論點。

### SD09 Agarwal, J.-H. Kim, Pande, Heo — TVLSI 2018，supply-regulated ring PLL 的零功耗前饋 spur 消除（App）
- 65 nm；第 1/2 次 spur 諧波消除 19.5/13 dB；oscillator gain 1.5 GHz/V；消除後 −53 dBc；320 µW [M]。
- 對學生：supply-regulated PLL 中 regulator 本身就在迴路內，這種架構的 oscillator gain 等同 RO 對 supply 的敏感度 [H]。1.5 GHz/V 可作為 65 nm ring 的 Kvdd 量級參考。
- 注意：這裡的 spur 是 PLL 自身的 spur，不是外加 supply noise 造成的。

### SD10 Razavi — SSC Magazine 2022，"The Design of an LDO Regulator"（R）
- 以 5-GHz LC VCO 為負載，從相位雜訊預算推 LDO 規格：1.2→1.0 V、≤1 mW、PSRR 40 dB 到 10 MHz、50 nV/√Hz @1 MHz、相位雜訊惡化 ≤1 dB；28 nm SS corner 設計 [S]。
- 對學生：**最推薦先讀**（作者網站有 PDF）。它示範了「應用→規格」的推導，可直接改寫成學生專題的動機章節。

### SD11 GWT-PSI — TWEPP 2023，10.24 Gb/s "Power Supply Immune" TX（App）
- 65 nm imaging 製程；capless LDO + clock-cleaning PLL + SST driver（±0.6 V/100 Ω，7.2 mW）。
- PSRR −50 dB（<1 MHz）只出現在搜尋摘要轉述中；正式論文未找到。
- 對學生：最貼近「capless LDO 放進 serial TX」的完整例子，而且是較成熟的 65 nm 製程。

### SD12 4×224 Gb/s 單端 PAM-4 front-end — 130 nm SiGe BiCMOS（App）
- TX 與 RX 都用 pseudo-differential 結構加 dual-loop regulator 求高 PSR；PSR 數值在摘要截斷處之後。
- 作者、年份、刊名未讀到。
- 對學生：證明 RX front-end 也會放 regulator。但是 BiCMOS，電路參考價值低。

### SD13 KAIST — ISSCC 2022，LPDDR5 SIJ-cancelling clock distribution（Crit）
- 28 nm；6.4 Gb/s、60 mV 1 MHz supply noise 下 clock rms jitter 27.84→4.28 ps [M]；使用二階 adaptive filter，因為 clock path 的 supply→jitter 是非線性的。
- 對學生：另一條「不靠 LDO」的路線。數字可在報告中說明 supply noise 對 clock 的影響有多大（未處理時 27.84 ps rms）。

### SD14 Brownlee, Hanumolu, Mayaram, Moon — JSSC 2006，0.5–2.5 GHz supply-regulated PLL（A，0.18 µm，2014 前背景）
- 0.18 µm、1.8 V、3.29 ps rms @2.4 GHz、25 mW；量測注入 50 mV supply tone 看 jitter 惡化 [M]。
- 對學生：同製程、同供電電壓的直接前例（作者網站有 PDF）。

### SD15 黃楷翔（清大碩論，2007）— 具穩壓功能振盪器之 PLL（A，0.18 µm，2014 前背景）
- 0.18 µm、1.8 V，量測輸出 0.24–2.4 GHz；設計方法兼顧抗電源雜訊、調頻範圍、迴路頻寬與 jitter。
- 對學生：台灣同製程碩論，取得容易，可當實作細節的參考。

---

## §3 supply noise → jitter：有來源的數字與公式

### 3.1 公式（[H]：教科書窄頻 FM 近似，不是本次搜尋到的來源）
設 RO 中心頻率 f0、supply 敏感度 K_VDD（Hz/V），LDO 輸出端的正弦漣波振幅 A_out、頻率 f_n，且 RO 為 free-running 或 f_n 在 PLL loop bandwidth 之外：
- 頻率偏移峰值 Δf = K_VDD·A_out
- 調變指數（相位偏移峰值）β = Δf / f_n（rad）
- 單邊 spur ≈ 20·log10(β/2) dBc（β ≪ 1 才成立）
- 週期性 jitter 峰對峰 ≈ 2β / (2π·f0)
- A_out = A_in·10^(−PSRR/20)。所以**在窄頻區，有 LDO 與沒 LDO 的 spur dB 差就等於該頻率的 PSRR**。這讓「量 RO spur」可以當成一種應用層級的 PSRR 量測 [H]。
- 若 f_n 在 PLL loop bandwidth 內，PLL 會壓制這個雜訊 [O1]。所以 PLL 論文報的 spur（SD03、SD07、SD08）都會強調「near loop bandwidth」[H]。

K_VDD 的量級（有來源者）：
- SD14：full-swing VCO 頻率正比於 supply → K_VDD ≈ f0/VDD [H，由此敘述推得]。
- [P1]：5 GHz 振盪器 Kvcc ≈ 5.5 GHz/V（正規化約 1.1 /V，[H] 計算）。
- SD09：supply-regulated ring PLL 的 oscillator gain 1.5 GHz/V（65 nm）。

### 3.2 數字整理

| 來源 | 條件 | 數字 | M/S |
|---|---|---|---|
| SD03 | 22 nm ring PLL，50 mVpp 正弦漣波 | 最差 spur < −54 dBc；immunity 改善 31.4 dB | M |
| SD08 | 65 nm，50 mVpp，近 loop BW | spur < −33 dBc | M |
| SD07 | 65 nm，近 loop BW | 平均約 30 dB spur suppression | M |
| SD13 | 28 nm clock distribution，60 mV、1 MHz | rms jitter 27.84 ps（未消除）→ 4.28 ps | M |
| SD01 | DPLL | 可容忍 240 mVpp；碩論：50 mVpp 10 kHz 下 pp jitter 41.87→29.11 ps（不確定同晶片） | 未知 / M |
| SD09 | supply-regulated ring PLL | oscillator gain 1.5 GHz/V；spur 消除後 −53 dBc | M |
| SD10 | LDO for 5-GHz LC VCO（設計目標） | PSRR 40 dB 至 10 MHz；50 nV/√Hz @1 MHz；PN 惡化 ≤1 dB；≤1 mW | S |
| SD04 | 180 nm LDO + 5 級 RO | 24.8 µVrms（1 kHz–1 MHz）；period jitter −64~71% | S |
| SD11 | capless LDO in 10.24 Gb/s TX | PSRR −50 dB（<1 MHz，轉述） | 未知 |
| SD14 | 0.18 µm supply-regulated PLL | 3.29 ps rms @2.4 GHz；量測注入 50 mV supply tone | M |
| SD15? | 0.18 µm PLL（對應不確定） | 0.3% clock period / 1% VDD @2.4 GHz | M？ |
| [B1] | 0.13 µm、1 V PLL，10 mV、1 MHz VCO supply noise | 3.95 ps rms（calibrated）vs 8.22 ps（conventional） | M |
| [B2] | 45 nm link clock generator，regulated-replica regulator | PSR >22 dB 至 1 GHz（80 pF decap）；4.5 ps/100 mV | M |
| [B3] | CDR（模擬） | 容忍度 20 mV/10 MHz → 加 LDO 後 200 mV/10 MHz | S |
| [B6] | 0.13 µm PLL | < 0.07% f_vco / 1% VDD | 未知 |
| [P1] | 5 GHz 振盪器 | Kvcc ≈ 5.5 GHz/V | 專利 |

### 3.3 套到學生情境的試算（全部 [H]，假設值）
假設：0.18 µm 片上 5 級 inverter RO，VDD = 1.6 V（LDO 輸出），f0 = 500 MHz，且 f ∝ VDD → K_VDD ≈ 0.31 GHz/V。
- Vin 上有 50 mVpp（A_in = 25 mV）、1 MHz 漣波，LDO PSRR 40 dB → A_out = 0.25 mV → Δf ≈ 78 kHz → β ≈ 0.078 rad → spur ≈ −28 dBc，週期性 jitter 峰對峰 ≈ 50 ps（週期 2 ns）。
- 同樣漣波在 10 MHz，PSRR 若掉到 20 dB → 結果相同（−28 dBc）。因為 β ∝ A_out/f_n，頻率高 10 倍剛好抵掉 PSRR 少的 20 dB。
- 沒 LDO（PSRR 0 dB）、1 MHz：β ≈ 7.8 rad，已不是窄頻，RO 頻率會被掃動約 ±7.8 MHz（±1.6%）。
- 負載暫態的影響：LDO 輸出 droop 20 mV → RO 頻率瞬間偏移約 6.25 MHz（1.25%）。這把學生的暫態規格直接連到時脈品質。
- 結論 [H]：free-running RO 對 supply 非常敏感，所以在 0.18 µm 用 RO 當「supply noise 感測器」，訊號夠大、用頻譜儀就量得到。這正是它適合當 LDO demo 負載的原因。

---

## §4 對 0.18 µm 學生專題的啟示

### 4.1 能借用的
1. **「LDO 供電片上 RO，量 supply-induced spur」有沒有人做過？**
   - 有，但大多出現在 **PLL 論文**裡，而且 regulator 是 PLL 的一部分：SD03 注入 50 mVpp、SD08 注入 50 mVpp、SD14 在 0.18 µm 注入 50 mV tone、[B1] 注入 10 mV 1 MHz。
   - 以「獨立類比 LDO + RO 當應用負載」為題、最接近的是 SD04（180 nm，**只有模擬**）。
   - 本次搜尋**沒找到** 2014 後在 0.18 µm **實測**「類比 LDO → RO spur／jitter」的論文。所以這可以當學生專題的區隔點，但不能宣稱首創（搜尋僅限摘要層級，且只用了 42 次）。
2. **規格推導方法**：照 SD10 的流程，從 RO 的 K_VDD（可在晶片上掃 Vout、量 f 得到）和可接受的 spur，反推 PSRR(f) 與輸出雜訊規格。
3. **量測指標**（[H] 建議）：spur(dBc) 對 f_n 的曲線（有／無 LDO 的差就是 PSRR，見 §3.1）；負載步階時 RO 頻率的瞬時偏移；K_VDD（Hz/V）。這些只需要信號產生器、bias-T（或在 Vin 疊加漣波）和頻譜儀 [H]。
4. **背景與同製程參考**：SD14、SD15（0.18 µm、1.8 V）可寫進文獻回顧；SD06 是同製程的「不用 LDO」對照。

### 4.2 不能做或要避免的
1. **不要把專題包裝成「SerDes LDO」**。本次找到的兩個 0.18 µm 例子頻率範圍約 0.5–2.5 GHz（SD14）與 0.24–2.4 GHz（SD15），和 SD03 的 6.8–14 GHz、>100 Gb/s 差很遠。正確說法是「以 SerDes 時脈供電為應用動機，用片上 RO 示範 supply-noise→jitter 的改善」[H]。
2. **負載電流規格不匹配**：SerDes 時脈 rail 的功耗是 mW 等級（SD10 overhead ≤1 mW；SD08 整個 PLL 3.12 mW @1 V，約 3 mA [H 換算]；SD09 320 µW）。學生的 10–100 mA 比較像整個 TX／多 lane 的供電 [H]（但 SD11 的單一 driver 也只有 6 mA）。
   - 建議 [H]：RO 只當小電流的 demo 負載（數 mA），另外放可程式化電流負載跑 10–100 mA，並分別報告輕載和重載下的 PSRR 與 spur，因為 pass device 的工作點不同 [H]。
3. **高頻 PSRR**：SerDes 時脈在意的頻段到 10 MHz（SD10）甚至 1 GHz（[B2]），PLL loop BW 可 >100 MHz（SD03）。0.18 µm 類比 LDO 的迴路頻寬遠低於此，高頻段只能靠 on-chip CL（100 pF–1 nF）和 pass device 寄生耦合決定 [H]。報告中應誠實標出 PSRR 的有效頻段。
4. **Headroom 論點在 0.18 µm 較弱**：SD07、[B1] 的批評針對 1 V 左右的低壓先進製程。學生是 1.8→1.6 V（200 mV dropout），headroom 相對寬裕。但 100 mA 下的 200 mV dropout 需要很大的 PMOS，RO 也會因供電從 1.8 V 降到 1.6 V 而變慢約 11%（若 f ∝ V）[H]。SD08 的 source-follower 路線可作為討論對照。

### 4.3 會不會改變「純類比 vs hybrid」的選擇？
- **不會翻盤，反而加強純類比（或類比主導）的理由**，前提是學生用 SerDes／時脈當應用背景 [H]：
  - 時脈 rail 要的是寬頻 PSRR 與低雜訊（SD10、[P1]、[O1]）。
  - 數位 LDO 的 PSR 通常差：agent3 的 D03 在他人比較表中為 −5 dB @1 MHz。
  - 數位 LDO 的 limit cycle（agent3 D04）是週期性漣波，打進 RO 就會變成 spur [H]。
  - SD01 雖用 digital LDO，但必須額外加 supply-noise cancellation controller 才行。
- 若學生仍想做 hybrid（為了暫態），則用 RO 當 demo 負載會直接暴露數位迴路的漣波與 spur。這是風險，也可以是誠實的比較實驗 [H]。
- 可借用的 PSRR 加強手法：agent2 收錄的 0.18 µm feedforward supply-noise cancellation（A01 Park et al. JSSC 2014）與 adaptive ripple cancellation（A03 Lim et al.，65 nm）。

---

## §5 沒查完的項目與建議關鍵字

**沒查到或沒查完：**
1. 56／112／224 Gb/s **CMOS（FinFET）** transceiver 論文中描述 LDO 的段落。摘要層級幾乎不提 LDO，可能只在全文的 power/clocking 章節 [H]。本次只找到 SD02（外接 LDO）、SD12（SiGe）。
2. CMOS RX 的 CTLE／slicer 用 LDO 供電的實例：沒找到。
3. 2014 後 0.18 µm **實測**的「LDO → RO／PLL spur」論文：沒找到（只有 SD04 模擬、SD06 數字未讀）。
4. 需要開全文才能確認：SD03 的 regulator 拓樸；SD11 的 PSRR 與 LDO 電流；SD12 的 PSR 數值、作者與年份；SD13 的作者與期刊版；SD15 是否就是「0.3% period / 1% VDD」那篇；SD04 作者。
5. [B2] IBM regulated-replica regulator 的正確年份與作者（各鏡像頁不一致）。

**另見（找到但未列入 CSV）：**
- Chae, Jeong, Choi, "Design and Comparative Study of Voltage Regulation-Based 2-Tap Flexible Feed-Forward Equalizer for Voltage-Mode Transmitters," IEEE Access 2022（以 supply/ground regulation 調 FFE 強度與擺幅；2.23 pJ/bit @20 Gb/s 為**模擬**）。
- S. S. Nagam（指導 P. Kinget），Columbia 博士論文 2020（Academic Commons 開放）：sub-sampling ring PLL 的 feed-forward noise cancellation；摘錄稱 supply-induced noise 壓低 19.5 dB、jitter 降 1.4 倍、65 nm（注意：與 SD09 的 19.5 dB 是不同數字，只是巧合）。
- Urso & Serdijn, IEEE TCAS-I 2020：DC-DC 供電 LC oscillator 的 LDO 與 spur reduction（spur 降 27 dB），非 SerDes。
- 12.5 Gb/s 半速率 CDR + 1:2 DEMUX，0.18 µm，電子學報 2014（rms jitter 1.9 ps）：摘錄未提 regulator，故未收。

**建議關鍵字（給下一輪有全文權限時）：**
- `"supply-regulated" ring PLL serial link`、`"split-tuned" supply regulated PLL`、`"replica" regulator clock generator PSR`
- `on-die LDO SerDes PSIJ`、`"clock LDO" transceiver FinFET`、`"VDDA" LDO PAM4 ISSCC`
- `ring VCO "supply sensitivity" "%/%"` 或 `"fs/mV"`、`"supply noise sensitivity" MDLL`
- `"supply-induced spur" LDO ring oscillator 180nm measurement`
- `TWEPP 2023 GWT-PSI JINST`（找 SD11 正式論文）
- 台灣學位論文：`穩壓器 鎖相迴路 0.18 電源雜訊`、`LDO 振盪器 電源抑制 量測`（清大、交大、台大 etd 系統）
