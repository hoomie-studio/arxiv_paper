# Arxiv 自動化轉譯原子操作 (v3.0 穩定版)

請嚴格遵守以下原子操作，執行過程中禁止回報完成，直到動作 7 結束。

## 第一階段：環境執行與驗證
【動作 1】：執行 PowerShell 指令（使用已驗證的 3.13 路徑）：
C:\Users\folow\AppData\Local\Programs\Python\Python313\python.exe C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\arxiv_downloader.py --mode collect

【動作 1.1】：實體檔案檢查：
powershell -Command "if (!(Test-Path 'C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_task.md')) { throw '檔案不存在' }; if ((Get-Item 'C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_task.md').Length -eq 0) { throw '檔案內容為空' }"

## 第二階段：規則與數據載入
【動作 2】：讀取 "C:\Users\folow\.openclaw\workspace\skills\STUDY\SKILL.md" 並內化為科普轉譯準則。

【動作 3】：使用 read_file 讀取 "C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_task.md"。

## 第三階段：核心轉譯與暫存
【動作 4】：專家轉譯：根據動作 2 的規則，將動作 3 的內容轉譯為白話科普摘要。

【動作 5】：優先調用 write_file 將摘要寫入 "C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_result.md"。

## 第四階段：自動歸檔與合併 (Paperbot 整合)
【動作 6】：執行合併歸檔指令：
C:\Users\folow\AppData\Local\Programs\Python\Python313\python.exe C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\arxiv_manager.py --mode merge

【動作 7】：任務完成，在對話中呈現摘要結果。