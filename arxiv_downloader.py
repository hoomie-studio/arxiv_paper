import os
import re
import sys
import requests
import datetime
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin
from markitdown import MarkItDown

# 強制控制台輸出為 UTF-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- 設定區域 ---
SEARCH_URL = (
    "https://arxiv.org/search/advanced?"
    "advanced=&terms-0-operator=AND&terms-0-term=Reconstruction&"
    "terms-0-field=title&classification-computer_science=y&"
    "classification-physics_archives=all&classification-include_cross_list=include&"
    "date-filter_by=past_12&date-year=&"
)

# 統一儲存路徑
BASE_PATH = r"C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads"
# 移除 OUTPUT_DIR (arxiv_sections)，直接使用 BASE_PATH
HISTORY_FILE = os.path.join(BASE_PATH, "arxiv_history.md")
TEMP_TASK = os.path.join(BASE_PATH, "temp_task.md")
TEMP_RESULT = os.path.join(BASE_PATH, "temp_result.md")
SUMMARY_FILE = os.path.join(BASE_PATH, "paper_summary.md")

BASE = "https://arxiv.org"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; section-extractor/1.0)"}

class ArxivFullDownloader:
    def __init__(self, history_file):
        self.history_file = history_file
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.md_converter = MarkItDown()
        # 只確保基礎 downloads 資料夾存在
        if not os.path.exists(BASE_PATH):
            os.makedirs(BASE_PATH)

    def fetch(self, url):
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.text

    def get_read_history(self):
        if not os.path.exists(self.history_file):
            return set()
        with open(self.history_file, "r", encoding="utf-8") as f:
            content = f.read()
            return set(re.findall(r'ID: ([\d.]+)', content))

    def get_first_paper_info(self, search_url):
        print(f"[*] 正在搜尋論文...")
        html = self.fetch(search_url)
        soup = BeautifulSoup(html, "html.parser")
        results = soup.select("li.arxiv-result")
        if not results:
            raise RuntimeError("找不到搜尋結果")
        
        read_history = self.get_read_history()
        for result in results:
            abs_link_el = result.select_one('p.list-title a[href*="/abs/"]')
            if not abs_link_el: continue
            abs_url = urljoin(BASE, abs_link_el.get("href"))
            arxiv_id = abs_url.split('/')[-1]
            if arxiv_id in read_history:
                print(f"[跳過] 已讀: {arxiv_id}")
                continue
                
            title_el = result.select_one("p.title")
            title = title_el.get_text(" ", strip=True)
            return {"abs_url": abs_url, "title": title, "arxiv_id": arxiv_id}
        return None

    def get_html_url(self, abs_url):
        html = self.fetch(abs_url)
        soup = BeautifulSoup(html, "html.parser")
        html_link_el = soup.select_one('a[href*="/html/"]')
        return urljoin(BASE, html_link_el.get("href")) if html_link_el else None

    def extract_sections_html(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        sections = soup.find_all("h2", class_="ltx_title_section")
        content_list = []
        for section in sections:
            if "abstract" in section.get_text().lower(): continue
            section_parts = [str(section)]
            for sibling in section.find_next_siblings():
                if isinstance(sibling, Tag) and sibling.name == "h2": break
                section_parts.append(str(sibling))
            content_list.append("\n".join(section_parts))
        return "\n".join(content_list)

    def save_to_temp_task(self, paper_info, html_body):
        # 使用 BASE_PATH 存放臨時 HTML，轉換後即刪除
        temp_html_path = os.path.join(BASE_PATH, "temp_processing.html")
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(f"<html><body>{html_body}</body></html>")

        print(f"[*] 正在轉換 Markdown 並寫入 temp_task.md...")
        result = self.md_converter.convert(temp_html_path)
        markdown_content = result.text_content

        with open(TEMP_TASK, "w", encoding="utf-8") as f:
            f.write(f"# 今日待處理論文任務\n\n")
            f.write(f"## 文獻名稱\n{paper_info['title']}\n\n")
            f.write(f"- URL: {paper_info['abs_url']}\n")
            f.write(f"- ID: {paper_info['arxiv_id']}\n")
            f.write(f"### 論文內容:\n\n{markdown_content}")
        
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)

    def update_history(self, paper_info, status="[PENDING]"):
        fetch_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(f"\n---\n## {paper_info['title']}\n")
            f.write(f"- ID: {paper_info['arxiv_id']}\n")
            f.write(f"- URL: {paper_info['abs_url']}\n")
            f.write(f"- 狀態: {status} ({fetch_time})\n")

    def validate_and_fix_format(self, content):
        if "## 文獻名稱" in content:
            return True, content
        return False, content

    def mode_merge(self):
        target_file = TEMP_RESULT if os.path.exists(TEMP_RESULT) else TEMP_TASK
        if not os.path.exists(target_file):
            print(f"[!] 找不到暫存檔")
            return
            
        with open(target_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
            
        success, final_content = self.validate_and_fix_format(raw_content)
        if not success:
            print("[!] 格式校驗失敗")
            return
            
        with open(SUMMARY_FILE, "a", encoding="utf-8") as sf:
            sf.write(f"\n\n# 歸檔時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            sf.write(final_content)
            
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as hf:
                history = hf.read()
            titles = re.findall(r'## 文獻名稱\n(.*?)\n', final_content)
            for title in titles:
                title = title.strip()
                history = re.sub(rf"## {re.escape(title)}.*?\[PENDING\]", 
                                 lambda m: m.group(0).replace("[PENDING]", "[已完成摘要]"), 
                                 history, flags=re.DOTALL)
            with open(self.history_file, "w", encoding="utf-8") as hf:
                hf.write(history)
                
        for f in [TEMP_TASK, TEMP_RESULT]:
            if os.path.exists(f): os.remove(f)
        print(f"[OK] 摘要已歸檔至 {SUMMARY_FILE}")

    def run(self):
        paper = self.get_first_paper_info(SEARCH_URL)
        if not paper:
            print("[!] 沒有新論文。")
            return

        html_url = self.get_html_url(paper['abs_url'])
        if not html_url:
            print(f"[-] {paper['arxiv_id']} 無 HTML 版本。")
            return

        print(f"[*] 正在處理: {paper['title']}")
        raw_html = self.fetch(html_url)
        extracted_html = self.extract_sections_html(raw_html)
        self.save_to_temp_task(paper, extracted_html)
        self.update_history(paper)
        print(f"[成功] 任務已更新至 downloads 目錄。")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["collect", "merge"], default="collect")
    args = parser.parse_args()

    downloader = ArxivFullDownloader(HISTORY_FILE)
    
    if args.mode == "collect":
        downloader.run()
    elif args.mode == "merge":
        downloader.mode_merge()