# LOG（只增不改，時間由 `date -u` 取得）

- 2026-11-02 16:39:40 UTC — Stage 0 開始。工作目錄決定為 repo `Allenstar2/abc` 的 `ldo-research/` 子目錄（理由見 DECISIONS.md D-001）。
- 2026-11-02 16:39:40 UTC — `apt-get install ngspice` 成功：ngspice-42。clone spice_model_collections（commit 4a64198）。
- 2026-11-02 16:39:40 UTC — inverter DC 測試跑通：VM = 0.872 V（VDD=1.8 V，Wn/Wp = 1u/2u，L=0.18u）。ngspice 以 BSIM3v1 碼解析 version=3.1；改成 3.3.0 在 L=1u 單點 OP 下 gm/gds/Id 完全相同（gm=598.8 µS, gds=7.59 µS, Id=90.9 µA @Vgs=0.7, Vds=0.9）。
- 2026-11-02 16:44:52 UTC — 元件特性完成（DEVICE_CHAR.md）。發現：PMOS L=0.18 在 Vsd=0.2V 時 gm/gds≈2；pass device 100mA@200mV 需 W≈1.3–3mm 且處 triode。啟動 4 個文獻 subagent（hybrid/Leduc、analog capless、digital+review+FoM 批評、0.18µm 學生可行）。
- 2026-11-02 16:48:40 UTC — REF-A 建好。手算 vs 模擬（Imin=50µA, Cc=3pF, CL=100pF）：輕載 DC 增益 52.5 vs 52.3 dB，UGF 2.55 vs 2.42 MHz，PM ~29° vs 28.1°；滿載 DC 33.7 vs 33.8 dB，UGF 2.68 vs 2.65 MHz。穩定度掃描 126 組完成（s1_refA_sweep.json），最差 PM 都在最輕載；CL=1nF 明顯更難補償。
