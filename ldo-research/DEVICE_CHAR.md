# 元件特性（模擬，PTM 180nm，ngspice-42，27 °C）

腳本：`sim/scripts/s0_device_char.py`，數據：`sim/results/s0_device_char.json`，圖：`sim/figs/s0_device_char.png`。
所有數字皆為 [X]（本次模擬），且只代表這個 PTM 模型的外插行為，**不是**任何真實製程。

## 1. 模型本身的限制

- `.model` 寫 `level=49 version=3.1`，ngspice-42 印出 `BSIM3v1 (3.1)`，也就是用舊版 BSIM3v1 程式碼。
  把 version 改成 3.3.0 後，在 NMOS W/L=10u/1u、Vgs=0.7、Vds=0.9 這一點 gm、gds、Id 完全相同（gm=598.8 µS、gds=7.59 µS、Id=90.9 µA）[X]。
  只驗了一個點，不代表全域相同（存檔：`sim/results/s11_misc_checks.json`）。**LTspice 對 level 49 的實作可能不同**，學生在 LTspice 重跑時數字可能差異，這點未驗證 [H]。
- `lmin = lmax = 0.18 µm`：ngspice 不會因 L 超出範圍而報錯，但 L ≠ 0.18 µm 的行為完全是 BSIM3 物理方程式的外插，沒有實測擬合。
- 模型含 `tref/xl/rd/rs/...` 等 ngspice BSIM3v1 不認得的參數（被忽略），對結果影響未知 [H]。

## 2. 量到的行為（W/L = 10，|Vds| = 0.6 V，gm/Id ≈ 10 V⁻¹）

| 元件 | L (µm) | Vth (V) | Id/(W/L) @ gm/Id=10 (µA) | gm/gds @ gm/Id=10 | gm/gds @ \|Vgs\|=0.6, \|Vds\|=0.2 | 同, \|Vds\|=0.9 |
|---|---|---|---|---|---|---|
| NMOS | 0.18 | 0.413 | 4.99 | 11.8 | 6.7 | 11.4 |
| NMOS | 0.5 | 0.495 | 4.09 | 59.2 | 31.7 | 69.5 |
| NMOS | 1.0 | 0.446 | 3.92 | 96.9 | 20.1 | 101.1 |
| PMOS | 0.18 | 0.278 | 1.83 | 14.4 | 2.1 | 10.1 |
| PMOS | 0.5 | 0.473 | 1.17 | 37.7 | 34.5 | 58.4 |
| PMOS | 1.0 | 0.446 | 1.02 | 75.0 | 42.3 | 99.1 |

觀察：
1. **趨勢合理**：gm/gds 隨 L 增加（NMOS 12 → 59 → 97；PMOS 14 → 38 → 75），與長通道 ro ∝ L 的預期方向一致。
2. **Vth 對 L 不單調**：NMOS 0.41 → 0.50 → 0.45 V，PMOS 0.28 → 0.47 → 0.45 V。這來自模型的 reverse short-channel (Nlx) 與 DIBL (Dvt0, Eta0) 項的外插。PMOS L=0.18 µm 的 Vth 在 |Vds|=0.6 V 只有 0.28 V，代表 DIBL 很強（PMOS `Eta0 = 8.5`）。
   → 用 L=0.18 µm 的 PMOS 當 pass device 時，Vth 會隨 Vsd 大幅變動，推測這會讓「關不掉」的漏電與輕載行為對 Vin 很敏感 [D/H，未做 Vin 掃描；高溫輕載漏電失效見 ANALYSIS.md A1]。
3. **L = 0.18 µm 的 PMOS 在 |Vds| = 0.2 V 時 gm/gds 只有 2.1**（|Vgs|=0.6 V）。LDO 規格 Vin−Vout = 200 mV，pass device 正好在這區 → pass stage 增益很低。
4. 結論：類比偏壓/增益級用 L = 0.5–1 µm，結果只看趨勢；任何「增益 xx dB」只在這個模型內成立。

## 3. Pass device 尺寸（PMOS，L = 0.18 µm，Vsd = 0.2 V，27 °C）

| Vg (V)（Vsg = 1.8−Vg） | 0.0 | 0.2 | 0.4 | 0.6 | 0.8 |
|---|---|---|---|---|---|
| Id / (W = 1000 µm) (mA) | 93.6 | 84.8 | 74.6 | 63.0 | 49.8 |

→ 在 Vin−Vout = 200 mV、閘極能被拉到 0.4 V 時，100 mA 需要 W ≈ 1.34 mm；留溫度與製程餘裕需 ~2–3 mm [X][D]。
這時 pass device 處於 **triode**（Vov ≈ 1 V ≫ Vsd = 0.2 V），三極區 gm/gds ≈ Vsd/(Vov−Vsd) < 1 [D]，
所以滿載時 pass stage 幾乎沒有電壓增益，迴路增益幾乎全靠 EA。這是本規格（200 mV dropout、100 mA）最根本的限制之一。
