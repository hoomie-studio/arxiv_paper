# Arxiv 自動化轉譯原子操作：Summary + Study Mode 雙階段版（OpenClaw 穩定版）

請嚴格遵守以下原子操作。執行過程中不要中途回報完成；只有動作 11 結束後才回覆結果。

重要規則：
- 執行 Python 時，直接呼叫完整 Python exe 與腳本路徑。
- 不要把 PowerShell 檢查指令當成 Python 或 Markdown 內容執行。
- 若某個檔案不存在，請直接停止並回報缺少哪個檔案，不要跳到下一步。
- 不要把 temp_task.md 當作摘要結果寫入或合併。

## 第一階段：爬蟲與任務檢查
【動作 1】：執行論文抓取。請用執行命令工具直接執行下列命令：
C:\Users\folow\AppData\Local\Programs\Python\Python313\python.exe C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\arxiv_downloader.py --mode collect
銜接要求：執行完畢後，繼續動作 1.1，不要回報完成。

【動作 1.1】：使用檔案讀取或檔案檢查工具確認以下檔案存在且內容不為空：
C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_task.md
如果不存在或為空，立刻停止並回報「temp_task.md 未產生」，不要繼續摘要。
銜接要求：檢查通過後，繼續動作 2，不要回報完成。

## 第二階段：Summary Mode 生成
【動作 2】：讀取 Summary 規則：
C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\summary.md
銜接要求：讀取後，繼續動作 3，不要回報完成。

【動作 3】：讀取論文原始任務：
C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_task.md
銜接要求：讀取後，繼續動作 4，不要回報完成。

【動作 4】：根據 summary.md，產出段落化 Summary Mode 摘要。請嚴格保留 summary.md 指定的 Markdown 標題，不要輸出 JSON，不要輸出額外說明。
銜接要求：生成後，繼續動作 5，不要回報完成。

【動作 5】：使用 write_file 將 Summary Mode 摘要寫入：
C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_summary.md
寫入後，使用檔案讀取或檔案檢查工具確認 temp_summary.md 存在且不為空。
銜接要求：檢查通過後，繼續動作 6，不要回報完成。

## 第三階段：Study Mode 生成
【動作 6】：讀取 Study Mode 規則：
C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\studymode.md
銜接要求：讀取後，繼續動作 7，不要回報完成。

【動作 7】：再次使用動作 3 的論文內容，並可參考 temp_summary.md，產出 Study Mode 學習內容。請包含分類關鍵字、學習路徑、先備知識、重要名詞、脈絡梳理、方法流程、圖表導讀、觀念確認、3 題理解檢查與延伸閱讀。
銜接要求：生成後，繼續動作 8，不要回報完成。

【動作 8】：使用 write_file 將 Study Mode 內容寫入：
C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_studymode.md
寫入後，使用檔案讀取或檔案檢查工具確認 temp_studymode.md 存在且不為空。
銜接要求：檢查通過後，繼續動作 9，不要回報完成。

## 第四階段：合併、渲染與發布
【動作 9】：再次確認以下兩個檔案都存在且不為空：
C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_summary.md
C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_studymode.md
如果任一檔案不存在或為空，停止並回報缺少的檔案，不要執行 merge。
銜接要求：檢查通過後，繼續動作 10，不要回報完成。

【動作 10】：執行合併、渲染與 GitHub Pages 更新。請用執行命令工具直接執行下列命令：
C:\Users\folow\AppData\Local\Programs\Python\Python313\python.exe C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\arxiv_studymode.py --mode merge
銜接要求：執行完畢後，繼續動作 11。

【動作 11】：任務完成後，在對話中回報：
1. 本次論文中文名稱
2. 一句話核心
3. temp_summary.md 是否成功寫入
4. temp_studymode.md 是否成功寫入
5. merge/render/push 是否成功