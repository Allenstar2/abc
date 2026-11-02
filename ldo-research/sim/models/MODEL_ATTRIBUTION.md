# 模型出處與授權

- 檔案：`180nm_bulk.pm`（未修改，逐位元複製）
- 來源：SJTU-YONGFU-RESEARCH-GRP / spice_model_collections，`ptm/180nm_bulk.pm`
  - https://github.com/SJTU-YONGFU-RESEARCH-GRP/spice_model_collections
  - clone 時 commit：`4a641982d35b5f997459914ea9e6624e3fd17419`（2026-10-31）
- 該 collection 授權：Creative Commons Attribution 4.0 International (CC BY 4.0)
  https://creativecommons.org/licenses/by/4.0/
- 原始模型：Predictive Technology Model (PTM)，Arizona State University Nanoscale Integration and Modeling (NIMO) Group，
  檔頭寫「Predictive Technology Model Beta Version, 180nm」。https://ptm.asu.edu/
- 重要限制（詳見 `../DEVICE_CHAR.md`）：
  - BSIM3 (level 49, version=3.1)；ngspice-42 會以 BSIM3v1 程式碼執行。
  - `lmin = lmax = 0.18 µm`：本模型只為 L=0.18 µm 擬合，長通道行為是外插。
  - 沒有 corner、沒有 mismatch 統計、沒有 well/ESD/電阻/電容等 PDK 元件。不是任何真實 foundry 製程，**不可用來宣稱可下線**。
