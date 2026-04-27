import os
import re
import sys
import markdown
import datetime
import subprocess

# 強制控制台輸出為 UTF-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- 配置區 ---
# 1. GitHub 倉庫設定
GITHUB_REMOTE_URL = "https://github.com/你的帳號/你的新倉庫.git" 

# 2. 路徑設定 (請確保與 arxiv_downloader.py 一致)
REPO_PATH = r"C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs"
BASE_PATH = os.path.join(REPO_PATH, "downloads")
OUTPUT_HTML = os.path.join(REPO_PATH, "index.html")

HISTORY_FILE = os.path.join(BASE_PATH, "arxiv_history.md")
TEMP_TASK = os.path.join(BASE_PATH, "temp_task.md")
TEMP_RESULT = os.path.join(BASE_PATH, "temp_result.md")
SUMMARY_FILE = os.path.join(BASE_PATH, "paper_summary.md")

# --- 功能模組 ---

def validate_and_fix_format(content):
    """學習自 paperbot：寬鬆校驗，只要有內容就通過，並自動修正標題"""
    if not content.strip():
        return False, ""
    
    # 檢查是否具備基本標題格式，若無則自動補強，確保 Swiper 能正確切割卡片
    if "## 文獻名稱" not in content:
        print("[!] 偵測到摘要缺少標準標題，正在自動修正格式...")
        content = f"## 文獻名稱\n(AI 自動產生標題)\n\n" + content
    return True, content

def render_swiper_html():
    """將 SUMMARY_FILE 內的所有摘要轉換為 Swiper 幻燈片網頁"""
    if not os.path.exists(SUMMARY_FILE):
        print(f"[!] 找不到 {SUMMARY_FILE}，無法渲染 HTML。")
        return

    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        full_md = f.read()

    # 使用「## 文獻名稱」作為切割點，將每篇論文切成一個 Slide
    papers_raw = re.split(r'(?=## 文獻名稱)', full_md)
    all_slides_html = ""

    for p in papers_raw:
        if not p.strip() or "## 文獻名稱" not in p:
            continue
        
        # 轉換 Markdown 為 HTML (支援換行與表格)
        body_html = markdown.markdown(p, extensions=['extra', 'nl2br'])
        
        # 封裝進 Swiper Slide 容器
        slide = f"""
        <div class="swiper-slide">
            <div class="card">
                {body_html}
            </div>
        </div>
        """
        all_slides_html += slide

    # Swiper 樣式表 (深色背景與高質感卡片)
    style = """
    :root { --primary-color: #ff6b6b; --bg-color: #121212; --card-bg: #1e1e1e; }
    body { background-color: var(--bg-color); color: #e0e0e0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; }
    .swiper { width: 100%; height: 100vh; }
    .swiper-slide { display: flex; justify-content: center; align-items: center; padding: 20px; box-sizing: border-box; }
    .card { 
        background: var(--card-bg); padding: 40px; border-radius: 20px; 
        max-width: 900px; width: 100%; max-height: 85vh; overflow-y: auto;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5); border-left: 10px solid var(--primary-color);
        line-height: 1.6; position: relative;
    }
    h2 { color: var(--primary-color); font-size: 2em; border-bottom: 1px solid #333; padding-bottom: 15px; }
    h3 { color: #4ecdc4; margin-top: 25px; }
    a { color: #f9d423; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; }
    code { background: #333; padding: 2px 5px; border-radius: 4px; }
    /* 滾動條樣式 */
    .card::-webkit-scrollbar { width: 8px; }
    .card::-webkit-scrollbar-thumb { background: #444; border-radius: 10px; }
    """

    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Arxiv AI 論文速報</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css"/>
        <style>{style}</style>
    </head>
    <body>
        <div class="swiper">
            <div class="swiper-wrapper">
                {all_slides_html}
            </div>
            <div class="swiper-pagination"></div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
        <script>
            const swiper = new Swiper('.swiper', {{
                direction: 'vertical',
                mousewheel: true,
                keyboard: true,
                speed: 800,
                pagination: {{ el: '.swiper-pagination', clickable: true }},
            }});
        </script>
    </body>
    </html>
    """

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"[Success] HTML 渲染完成: {OUTPUT_HTML}")

def git_push_auto():
    """自動執行 Git 同步動作"""
    print("[Git] 正在同步至 GitHub...")
    try:
        # 切換到 Repo 目錄
        os.chdir(REPO_PATH)
        
        # 檢查是否為 git 倉庫
        if not os.path.exists(os.path.join(REPO_PATH, ".git")):
            print("[Error] 偵測到目標路徑非 Git 倉庫，請先執行 git init。")
            return

        subprocess.run(["git", "add", "."], check=True)
        commit_msg = f"Auto-update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        # 允許 commit 失敗 (若無變動時)
        subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
        
        # 推送至遠端
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[Git] GitHub 同步成功！")
    except Exception as e:
        print(f"[Git Error] 同步失敗: {e}")

def mode_merge():
    """核心合併邏輯：合併暫存 -> 更新歷史紀錄 -> 渲染 HTML -> Git 推送"""
    # 決定讀取哪個暫存檔
    target_file = TEMP_RESULT if os.path.exists(TEMP_RESULT) else TEMP_TASK
    if not os.path.exists(target_file):
        print("[!] 找不到任何待處理的暫存摘要檔案。")
        return

    print(f"[*] 正在處理檔案: {target_file}")
    with open(target_file, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # 1. 寬鬆格式校驗
    success, final_content = validate_and_fix_format(raw_content)
    if not success:
        print("[!] 檔案內容為空，取消合併。")
        return

    # 2. 歸檔至總表
    with open(SUMMARY_FILE, "a", encoding="utf-8") as sf:
        sf.write(f"\n\n# 歸檔日期: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        sf.write(final_content)
    print(f"[OK] 已歸檔至 {SUMMARY_FILE}")

    # 3. 更新歷史紀錄狀態 (由 [PENDING] 轉為 [已完成])
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as hf:
            history = hf.read()
        
        # 提取摘要中的標題 (基於 ## 文獻名稱 後的一行)
        titles = re.findall(r'## 文獻名稱\n(.*?)\n', final_content)
        for title in titles:
            title_clean = title.strip()
            # 尋找歷史紀錄中對應標題的 [PENDING] 狀態並替換
            history = re.sub(rf"## {re.escape(title_clean)}.*?\[PENDING\]", 
                             lambda m: m.group(0).replace("[PENDING]", "[已完成摘要]"), 
                             history, flags=re.DOTALL)
        
        with open(HISTORY_FILE, "w", encoding="utf-8") as hf:
            hf.write(history)
        print("[OK] 歷史紀錄狀態已更新。")

    # 4. 渲染 HTML
    render_swiper_html()

    # 5. Git 推送
    git_push_auto()

    # 6. 清理暫存檔
    for f in [TEMP_TASK, TEMP_RESULT]:
        if os.path.exists(f):
            os.remove(f)
            print(f"[*] 已清理暫存檔: {f}")

if __name__ == "__main__":
    # 此腳本專注於 merge 模式
    mode_merge()