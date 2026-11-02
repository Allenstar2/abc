# literature CSV 欄位（UTF-8，逗號分隔，含逗號的欄位用雙引號）

id,first_author,authors_short,title,venue,year,doi,url,fulltext_status,fulltext_url,arch_class,process,vin_v,vout_v,imax_ma,iq_ua,cl_onchip,dropout_mv,deltaV_mv,deltaI_ma,edge_time,psrr,area_mm2,result_type,numbers_source,relevance,notes

- doi: 只填已驗證的 DOI（例如 10.1109/JSSC.2014.2xxxx）；無法驗證就留空並在 notes 寫「DOI 未驗證」
- url: 可開啟的頁面（IEEE Xplore document 頁、arXiv、典藏）
- fulltext_status: 全文-開放 / 全文-作者版 / 全文-學位論文 / 全文-出版社OA / 僅摘要 / 找不到
- arch_class: A(純類比) / B(類比主導雙迴路HLDO) / C(數位主導類比輔助) / D(純數位) / R(回顧/教學) / Mx(量測方法) / Crit(反面意見或限制) / 未確認
- 數字欄：只填實際讀到的值，附單位；未知留空。numbers_source: 全文 / 摘要 / 表格(他人比較表)
- result_type: M(實測) / S(模擬) / 未知
