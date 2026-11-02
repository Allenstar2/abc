#!/usr/bin/env bash
# 一鍵重跑所有模擬（需要 ngspice ≥ 42、python3、numpy、matplotlib、pandas+openpyxl(僅資料集統計)）
# 用法：bash sim/run_all.sh        （從 ldo-research/ 目錄或任意目錄執行皆可）
# 選用：DLDO 資料集統計需先 git clone https://github.com/mgseok/DLDO-survey ldo-research/ext/DLDO-survey
# 注意：腳本共用 sim/results/ 下的暫存檔名，請勿同時執行兩份。
set -euo pipefail
cd "$(dirname "$0")/scripts"
echo "[0] 元件特性 (DEVICE_CHAR.md)";            python3 s0_device_char.py > ../results/run_s0.txt
echo "[1] REF-A 穩定度掃描";                      python3 s1_refA_sweep.py > ../results/run_s1.txt
echo "[2] 手算 vs 模擬";                           python3 s2_hand_vs_sim.py | tee ../results/run_s2.txt
echo "[3] REF-A 完整特性 (Bode/PSRR/暫態/Iq/dropout)"; python3 s3_refA_char.py > ../results/run_s3.txt
echo "[4] 實驗 X2：邊沿時間與起點電流";             python3 s4_exp_edge.py | tee ../results/run_s4.txt
echo "[5] 實驗 X3：hybrid limit cycle / 大步階 / PSRR"; python3 s5_exp_hybrid.py | tee ../results/run_s5.txt
echo "[5b] hybrid 固定碼迴路增益";                  python3 s5b_hybrid_loop.py | tee ../results/run_s5b.txt
echo "[5c] slice 切換尖峰 vs 驅動邊沿、FO4";         python3 s5c_hybrid_glitch.py | tee ../results/run_s5c.txt
echo "[5d] 規格敏感度 Imax×CL"; python3 s8_sensitivity.py | tee ../results/run_s8.txt
echo "[6] 粗略 corner/溫度趨勢";                    python3 s6_corners.py > ../results/run_s6.txt
echo "[8] 實驗 X4：首選架構的 SRE";               python3 s9_sre.py | tee ../results/run_s9.txt
echo "[8b] SRE 參數掃描";                          python3 s9b_sre_sweep.py | tee ../results/run_s9b.txt
echo "[8c] 實驗 X5：VCO 供電漣波→jitter";             python3 s10_vco_supply.py | tee ../results/run_s10.txt
echo "[8d] 補充查核";                              python3 s11_misc_checks.py > ../results/run_s11.txt
echo "[8e] 第 1 輪審查反例重現（公平 B）";             python3 s12_fairB.py | tee ../results/run_s12.txt
echo "[9] LEARNING 實驗";                          python3 learn.py all > ../results/run_learn.txt
if [ -d ../../ext/DLDO-survey ]; then
  echo "[7] DLDO 資料集統計";                        python3 s7_dataset_stats.py | tee ../results/run_s7.txt
fi
echo "完成。圖在 sim/figs/，數據在 sim/results/*.json"
