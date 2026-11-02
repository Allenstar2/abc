# LOG（只增不改，時間由 `date -u` 取得）

- 2026-11-02 16:39:40 UTC — Stage 0 開始。工作目錄決定為 repo `Allenstar2/abc` 的 `ldo-research/` 子目錄（理由見 DECISIONS.md D-001）。
- 2026-11-02 16:39:40 UTC — `apt-get install ngspice` 成功：ngspice-42。clone spice_model_collections（commit 4a64198）。
- 2026-11-02 16:39:40 UTC — inverter DC 測試跑通：VM = 0.872 V（VDD=1.8 V，Wn/Wp = 1u/2u，L=0.18u）。ngspice 以 BSIM3v1 碼解析 version=3.1；改成 3.3.0 在 L=1u 單點 OP 下 gm/gds/Id 完全相同（gm=598.8 µS, gds=7.59 µS, Id=90.9 µA @Vgs=0.7, Vds=0.9）。
