# LOG（只增不改，時間由 `date -u` 取得）

- 2026-11-02 16:39:40 UTC — Stage 0 開始。工作目錄決定為 repo `Allenstar2/abc` 的 `ldo-research/` 子目錄（理由見 DECISIONS.md D-001）。
- 2026-11-02 16:39:40 UTC — `apt-get install ngspice` 成功：ngspice-42。clone spice_model_collections（commit 4a64198）。
- 2026-11-02 16:39:40 UTC — inverter DC 測試跑通：VM = 0.872 V（VDD=1.8 V，Wn/Wp = 1u/2u，L=0.18u）。ngspice 以 BSIM3v1 碼解析 version=3.1；改成 3.3.0 在 L=1u 單點 OP 下 gm/gds/Id 完全相同（gm=598.8 µS, gds=7.59 µS, Id=90.9 µA @Vgs=0.7, Vds=0.9）。
- 2026-11-02 16:44:52 UTC — 元件特性完成（DEVICE_CHAR.md）。發現：PMOS L=0.18 在 Vsd=0.2V 時 gm/gds≈2；pass device 100mA@200mV 需 W≈1.3–3mm 且處 triode。啟動 4 個文獻 subagent（hybrid/Leduc、analog capless、digital+review+FoM 批評、0.18µm 學生可行）。
- 2026-11-02 16:48:40 UTC — REF-A 建好。手算 vs 模擬（Imin=50µA, Cc=3pF, CL=100pF）：輕載 DC 增益 52.5 vs 52.3 dB，UGF 2.55 vs 2.42 MHz，PM ~29° vs 28.1°；滿載 DC 33.7 vs 33.8 dB，UGF 2.68 vs 2.65 MHz。穩定度掃描 126 組完成（s1_refA_sweep.json），最差 PM 都在最輕載；CL=1nF 明顯更難補償。
- 2026-11-02 16:52:51 UTC — agent1（hybrid/Leduc）與 agent4（0.18µm 可行）回報：學術網站全部被網路政策擋（403 CONNECT），0 篇全文；WebSearch 每回合額度被用完。Leduc 2025 = 未確認（僅摘要），書目 IEEE TCAS-I vol.72 pp.3733–3743，Xplore doc 10884555（頁碼來自二手引用）。實驗 X2（邊沿時間）完成：同一電路 0→100mA undershoot 從 748 mV(0.1ns) 到 21 mV(10→100mA, 1µs)。
- 2026-11-02 16:56:16 UTC — X3 hybrid 實驗完成：寬窗(15mA>slice 12.2mA)無 limit cycle；窄窗(6mA)在 20mA 負載出現 limit cycle，Vout p-p 190–229 mV。5→95mA 步階：REF-A 127 mV(100ns)/499 mV(1ns)，REF-B 313/238 mV(10/50MHz,100ns)/756 mV(1ns)。固定碼 PSRR@1kHz：REF-A −38 dB vs REF-B −18.8 dB(70mA)。固定碼迴路 DC 增益 16–23 dB(slice 開時)。corner 趨勢：125°C SF-like 輕載 Vout=1.6525（pass 漏電超過 200µA 洩放，調節失效）。agent2/agent3 完成。
- 2026-11-02 17:04:55 UTC — ANALYSIS.md（Stage 4）完成；s8 敏感度與 1nF 補償公平性檢查完成（500µA 洩放下趨勢不變）。X3e：slice 尖峰 82.6/71.4/34.5 mV（t_drv 1/30/300 ns）；PTM FO4 54–60 ps。run_all.sh 建立。
- 2026-11-02 17:07:41 UTC — X4 SRE：第一版固定 0.3 V 偏壓失敗（PTM PMOS L=0.18 DIBL 使偵測管靜態導通，Vout=Vin、Iq 3.59 mA）；第二版 replica 偏壓 L=0.18 仍因 DIBL 失配使 Mup 靜態半導通（Iq +94 µA、OP 改變）；第三版偵測管/replica 改 L=0.5 µm，靜態 gdn≈55 mV、Vin−gu≈55 mV（−40/27/125 °C）。
- 2026-11-02 17:10:24 UTC — 自我更正：ANALYSIS.md 原寫『SF buffer 只能把 pg 拉到 ~1.65 V』錯誤；重跑 SF-like 125°C OP：pg=1.759 V、ea=1.643 V、Vout=1.6525 V，失效原因是 pass 在 Vsg≈41 mV 仍漏 ~0.2 mA。learn.py 10 題完成（learn_answers.json）。X4 SRE 掃描：最佳 undershoot 改善 8–15%。GAPS.md 完成（保留 G1、G2(弱)，刪除 G3–G5）。
