# Arxiv Paper Library：CRON 自動流程提示詞

你現在要執行 Arxiv_cs 這個 skill 的每日自動流程。

非常重要：
- `arxiv_downloader.py` 只負責抓取論文與產生 `downloads/temp_task.md`。
- `arxiv_studymode.py` 只支援 `--mode merge` 與 `--mode render`。
- `arxiv_studymode.py` 不會呼叫模型，也沒有 `summary` 或 `studymode` 生成模式。
- Summary 與 Study Mode 的 Markdown 內容只能由 OpenClaw/Qwen 在對話中完成，再寫入暫存檔。
- Summary 與 Study Mode 內容必須由你這個 OpenClaw/Qwen 模型依照 prompt 生成，再用寫檔工具存成 Markdown。
- 不要用 PowerShell 內嵌長段 Markdown，也不要用 Python 自己假裝生成摘要。
- 每一步完成後才進入下一步；如果缺檔或檔案是空的，停止並回報，不要 merge。

## 固定路徑

Skill 目錄：
`C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs`

下載與暫存目錄：
`C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads`

Python：
`C:\Users\folow\AppData\Local\Programs\Python\Python313\python.exe`

## 動作 1：抓取一篇待處理論文

執行：

```powershell
C:\Users\folow\AppData\Local\Programs\Python\Python313\python.exe C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\arxiv_downloader.py --mode collect
```

完成後，檢查這個檔案是否存在且不是空檔：

`C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_task.md`

如果不存在或是空檔，請停止流程並回報「沒有可處理的新論文或抓取失敗」。

## 動作 2：讀取 Summary prompt

讀取：

`C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\summary.md`

這是 Summary Mode 的輸出規格。

## 動作 3：讀取論文內容

讀取：

`C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_task.md`

這是本次要摘要的論文內容與來源資訊。

## 動作 4：由模型生成 Summary Mode

請你作為 OpenClaw/Qwen 模型，依照 `summary.md` 的規格，根據 `temp_task.md` 的內容生成 Summary Mode Markdown。

注意：
- 這一步是模型生成文字，不是 Python 指令。
- 不要呼叫任何 Python 腳本來生成 Summary。
- 不要只把 `temp_task.md` 原文貼過去。
- 必須產生符合 `summary.md` 標題格式的繁體中文摘要。

生成完成後，把完整 Summary Markdown 寫入：

`C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_summary.md`

寫入後檢查檔案存在且不是空檔。

## 動作 5：讀取 Study Mode prompt

讀取：

`C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\studymode.md`

這是 Study Mode 的輸出規格。

## 動作 6：由模型生成 Study Mode

請你作為 OpenClaw/Qwen 模型，依照 `studymode.md` 的規格，根據 `temp_task.md` 的內容生成 Study Mode Markdown。

可以參考剛剛產生的：

`C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_summary.md`

但 Study Mode 不是 Summary 的重寫，必須補足：
- 30 秒看懂
- 先備知識
- 重要名詞，包含白話描述與意義
- 研究動機
- 方法流程
- 觀念確認
- 3 題理解檢查選擇題

注意：
- 這一步是模型生成文字，不是 Python 指令。
- 不要呼叫任何 Python 腳本來生成 Study Mode。
- 不要只把 `temp_task.md` 原文貼過去。
- 必須產生符合 `studymode.md` 標題格式的繁體中文學習內容。

生成完成後，把完整 Study Mode Markdown 寫入：

`C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_studymode.md`

寫入後檢查檔案存在且不是空檔。

## 動作 7：合併、渲染、推送

確認以下兩個檔案都存在且不是空檔：

`C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_summary.md`

`C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads\temp_studymode.md`

確認後執行：

```powershell
C:\Users\folow\AppData\Local\Programs\Python\Python313\python.exe C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\arxiv_studymode.py --mode merge
```

`merge` 會做三件事：
1. 把 Summary 與 Study Mode 合併進 `downloads/paper_summary.md`
2. 重新產生 `index.html`
3. 執行自動 Git push

如果 merge 回報缺少章節或缺少暫存檔，停止並回報錯誤，不要刪除暫存檔。

## 最終回報

流程完成後，請回報：
1. 文獻中文名稱
2. 一句話核心
3. `temp_summary.md` 是否已寫入
4. `temp_studymode.md` 是否已寫入
5. merge/render/push 是否成功
