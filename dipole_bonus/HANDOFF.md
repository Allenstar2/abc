# 交接：電磁學加分作業（電偶極 V 與 E，MATLAB）

> 給接手的 Claude / 本人看的進度紀錄。最後更新：2026-11-08（雲端 session 交接到本地）。
> 本地開始時對 Claude 說：「先讀 dipole_bonus/HANDOFF.md，接著做。」

## 1. 作業要求（來自老師投影片第 60 頁的手寫板書）

- 加分作業，**by MATLAB**，至少 3 個點
- 用手算的 V（V理）跟電腦算的 V（V電）比對，看是否相同
- 板書寫了 V → E = −∇V
- 表格欄位：點(P0~P2) | x,y | R,θ,φ | V理 | V電 | 誤差, 誤差%（橘框標「驗正確性」）
- **只取做得最好的 3 份加分** → 使用者要求做出跟同學的差異
- 繳交格式：Word 報告 + MATLAB code 全部壓成 `name.zip` 或 `name.rar`（name 換成自己的名字或學號）

## 2. 使用者背景

- 不會 MATLAB，用 **MATLAB Online**（MATLAB Drive）。
- 報告用繁體中文，照使用者的寫作習慣寫（skill：`my-writing-style`）。正式報告只套用標點和連接詞規則：
  - 逗號、句號、頓號用全形；冒號、問號、括號用半形 `:` `?` `( )`
  - 轉折只用「但」，不用然而、此外、因此、綜上所述
  - 常用「與」「及」「藉由」「使」，推測語氣用「推測」「可能」
- 回覆使用者用繁體中文。

## 3. 檔案（git 分支 `dipole-bonus`，沒有開 PR，`main` 沒動）

| 路徑 | 說明 |
|---|---|
| `dipole_bonus/dipole_main.m` | **唯一的程式檔**。Part 0~5，最後面有區域函數 `coulombE`、`unitE`（需要 MATLAB R2016b 以上） |
| `dipole_bonus/dipole_report.docx` | Word 報告，14 頁 |
| `dipole_bonus/results.txt` | 程式輸出的所有數值（`diary`） |
| `dipole_bonus/table_points.csv` | 表 1 資料 |
| `dipole_bonus/fig1~fig4_*.png` | 程式產生的 4 張圖（目前是 **Octave** 畫的） |
| `dipole_bonus/tools/build_report.js` | 產生 Word 報告的腳本（docx-js）。改報告內容就改這個檔再重跑 |
| `name.zip`（repo 根目錄） | 繳交用壓縮檔 = report + .m + results + csv + 4 張 png |

### 常用指令

```bash
# 重建 Word 報告（讀 dipole_bonus/fig*.png，輸出 dipole_bonus/dipole_report.docx）
node dipole_bonus/tools/build_report.js          # 需要 npm 套件 docx

# 重新打包 zip（在 repo 根目錄）
rm -f name.zip && zip -j name.zip dipole_bonus/dipole_report.docx dipole_bonus/dipole_main.m \
  dipole_bonus/results.txt dipole_bonus/table_points.csv dipole_bonus/fig*.png
```

- MATLAB：在 `dipole_bonus` 資料夾執行 `dipole_main`。產生的 png/txt/csv 會覆蓋現有的。
- Octave 測試：Octave 不支援把函數放在 script 最後面。要把「區域函數」那段移到檔案最前面、第一行加 `1;`，另存一份再跑（不要改原檔）。沒有螢幕的環境畫圖要用 `xvfb-run`。

## 4. 程式內容與已驗證的結果

參數：k = 8.99e9（手算與程式用同一個值）、q = 1 nC、d = 1 cm、p = 1e-11 C·m、kp = 0.0899 V·m²。
+q 在 (0,0,d/2)，−q 在 (0,0,−d/2)。V理 = 遠場公式 kp·cosθ/R²；V電 = 兩點電荷精確疊加。

| 點 | (x,y,z) m | R, θ, φ | V理 | V電 | 誤差 % |
|---|---|---|---|---|---|
| P0 近 | (0,0,0.02) | 0.02, 0°, — | 224.75 | 239.73333 | 6.2500 |
| P1 中 | (0.03,0.04,0.05) | 0.07071, 45°, 53.13° | 12.71378 | 12.69772 | 0.1265 |
| P2 遠 | (0.12,0.16,0.15) | 0.25, 53.13°, 53.13° | 0.86304 | 0.86283 | 0.0240 |

- **Part 2 E = −∇V**：中央差分 h = 1e-6，與庫侖定律差 < 1e-6 %。遠場 E 在 P0 誤差 12.11%（z 軸上的精確式 1 − (1 − (d/2R)²)²）。
- **Part 3 誤差 vs R/d**：相對誤差 ≈ |P₃(cosθ)/(4cosθ)|·(d/R)²，擬合斜率 θ = 0/50/80° 都是 −2.000。在 θ = 39.23°（cos²θ = 3/5，P₃ = 0）斜率是 −4（−3.9999）。全方向誤差 < 1% 需要 R/d ≥ 6.13（θ → 90° 最差，理論值 √37.5 ≈ 6.12）。z 軸上誤差剛好等於 (d/2R)²。
- **Part 4 垂直驗證**：contourc 取等位線切線，E 用庫侖定律（與 V 獨立）。14252 段，平均 89.8922°，最小 88.59°，99.78% 在 1° 以內。電場線用 RK4，沿 E 的單位向量積分。
- **Part 5**：R = 0.05、θ = 45°，φ = 0/37/90/180/270，V 都是 25.36264478。

**這些數字都只在 GNU Octave 8.4 跑過，還沒在 MATLAB 確認**。合併成單一檔案之後，只用「函數移到前面」的 Octave 測試版驗證過，`results.txt` 與拆檔版完全相同。

## 5. 報告結構（`build_report.js`）

封面（學號、姓名、年級、日期都是 ○○○ 待填）→ 一、動機與目的 → 二、理論（式 1~7，含 Legendre 展開與 4 個預測）→ 三、方法 → **四、程式說明**（程式 1~7 灰底 code block，各附「為什麼這樣寫」）→ 五、結果（表 1~5、圖 1~4）→ 六、討論（「對 X 的分析:」格式）→ 七、結論 → 參考文獻 → 附錄（表 6 檔案清單、執行方式）。

參考文獻（目前 3 篇）：
1. D. K. Cheng, *Field and Wave Electromagnetics*, 2nd ed., Addison-Wesley, 1989
2. D. J. Griffiths, *Introduction to Electrodynamics*, 4th ed., Cambridge Univ. Press, 2017
3. M. de Magistris, "A MATLAB-based virtual laboratory for teaching introductory quasi-stationary electromagnetics," *IEEE Trans. Educ.*, vol. 48, no. 1, pp. 81–88, 2005, doi: 10.1109/TE.2004.832872（從搜尋摘要查到，全文沒讀過）

[1][2] 要依使用者課堂實際用的課本調整。

## 6. 待辦

- [ ] **使用者還沒回答**：圖要留幾張？上一輪給的選項：
  1. 精簡成 2 張（圖 3 等位線＋電場線、圖 1 誤差 vs R/d），圖 4 改成一句數字，圖 2 刪掉或移到附錄，程式也只畫這 2 張（**我的建議**）
  2. 只留圖 3
  3. 4 張都留，程式用 `subplot` 合成一個視窗
  4. 維持現狀

  改圖之後，要同步改 `dipole_main.m`、`build_report.js`（圖號、表號、「第 X 節」的引用、附錄檔案表）、results，再重新打包 zip。
- [ ] 使用者在 MATLAB Online 跑 `dipole_main`，核對第 4 節的數字。可以把 MATLAB 畫的 png 換掉 Octave 版，再重建報告。
- [ ] 封面填學號、姓名、年級、日期；`name.zip` 改成老師要的檔名。
- [ ] 確認參考文獻的版本，並上 IEEE Xplore 核對 [3] 的頁碼與 DOI。
- [ ] 使用者想參考的 3 份 PDF，雲端 session 都抓不到（Notaros 的 MATLAB 習題清單 403、Notaros 期刊論文 colostate `~aam/pdf/journals/102.pdf` 403、UMD *Electrostatics with MATLAB* 講義 503）。請使用者用瀏覽器下載後提供，讀過再決定要不要加進參考文獻。**不要憑記憶寫它們的內容或書目。**
- [ ] 使用者說「說不出哪裡不好」。已加了程式說明，可能還有：圖的標籤是英文、理論推導像課本、篇幅偏長（14 頁）。

## 7. 注意事項

- 使用者要能自己講解內容（為什麼斜率 −2、39.23° 怎麼來的、為什麼 E 要用庫侖定律而不用 −∇V 來驗證垂直）。
- 報告是以使用者的名義交的，不要替使用者編造個人經歷或感想。
- commit 結尾要加 Co-Authored-By 等 attribution lines（依當下 session 的設定）。
