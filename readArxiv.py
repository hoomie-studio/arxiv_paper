import os
import re
import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin
import datetime
# 匯入 Microsoft MarkItDown
from markitdown import MarkItDown

# --- 設定區域 ---
SEARCH_URL = (
    "https://arxiv.org/search/advanced?"
    "advanced=&terms-0-operator=AND&terms-0-term=Reconstruction&"
    "terms-0-field=title&classification-computer_science=y&"
    "classification-physics_archives=all&classification-include_cross_list=include&"
    "date-filter_by=past_12&date-year=&"
)
# 設定下載路徑
BASE_PATH = r"C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads"
OUTPUT_DIR = os.path.join(BASE_PATH, "arxiv_sections")
HISTORY_FILE = os.path.join(BASE_PATH, "arxiv_history.md")
TEMP_TASK = os.path.join(BASE_PATH, "temp_task.md")
# ----------------

BASE = "https://arxiv.org"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; section-extractor/1.0)"}

class ArxivFullDownloader:
    def __init__(self, output_dir, history_file):
        self.output_dir = output_dir
        self.history_file = history_file
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.md_converter = MarkItDown() # 初始化 MarkItDown
        os.makedirs(self.output_dir, exist_ok=True)

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

    def update_history(self, paper_info):
        fetch_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(f"\n---\n## {paper_info['title']}\n")
            f.write(f"- ID: {paper_info['arxiv_id']}\n")
            f.write(f"- URL: {paper_info['abs_url']}\n")
            f.write(f"- 抓取時間: {fetch_time}\n")
            f.write(f"- 狀態: [已完成下載]\n")

    def get_first_paper_info(self, search_url):
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
            if arxiv_id in read_history: continue
                
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
        """擷取特定的 HTML 章節結構"""
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
        """使用 MarkItDown 將 HTML 轉為 Markdown 並儲存"""
        # 1. 將擷取的 HTML 暫存，以便 MarkItDown 讀取轉換
        temp_html_path = os.path.join(self.output_dir, "temp_extract.html")
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(f"<html><body>{html_body}</body></html>")

        # 2. 執行轉換
        result = self.md_converter.convert(temp_html_path)
        markdown_content = result.text_content

        # 3. 寫入 temp_task.md
        with open(TEMP_TASK, "w", encoding="utf-8") as f:
            f.write(f"# 今日待處理論文任務\n\n")
            f.write(f"## {paper_info['title']}\n")
            f.write(f"- URL: {paper_info['abs_url']}\n")
            f.write(f"- ID: {paper_info['arxiv_id']}\n")
            f.write(f"- 轉換時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"### 論文內容 (Markdown 格式):\n\n")
            f.write(markdown_content)
        
        # 移除過渡用的 HTML 暫存檔
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)

    def run(self):
        paper = self.get_first_paper_info(SEARCH_URL)
        if not paper:
            print("[!] 沒有新論文任務。")
            return

        html_url = self.get_html_url(paper['abs_url'])
        if not html_url:
            print(f"[-] {paper['arxiv_id']} 無 HTML 版本，跳過。")
            return

        print(f"[*] 正在下載: {paper['title']}")
        raw_html = self.fetch(html_url)
        extracted_html = self.extract_sections_html(raw_html)

        print(f"[*] 正在透過 MarkItDown 轉換為 Markdown...")
        self.save_to_temp_task(paper, extracted_html)
        
        self.update_history(paper)

        print("-" * 30)
        print(f"[成功] Markdown 任務已寫入: {TEMP_TASK}")
        print(f"[紀錄] 已更新 arxiv_history.md")

if __name__ == "__main__":
    downloader = ArxivFullDownloader(OUTPUT_DIR, HISTORY_FILE)
    downloader.run()