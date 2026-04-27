import os
import re
import sys
import html
import argparse
import markdown
import subprocess
from datetime import datetime

if sys.platform.startswith("win"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO_PATH = r"C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs"
BASE_PATH = r"C:\Users\folow\.openclaw\workspace\skills\Arxiv_cs\downloads"
OUTPUT_HTML = os.path.join(REPO_PATH, "index.html")
HISTORY_FILE = os.path.join(BASE_PATH, "paper_history.md")
TEMP_TASK = os.path.join(BASE_PATH, "temp_task.md")
TEMP_RESULT = os.path.join(BASE_PATH, "temp_result.md")
SUMMARY_FILE = os.path.join(BASE_PATH, "paper_summary.md")
GITHUB_REMOTE_URL = "https://github.com/hoomie-studio/arxiv_paper.git"

REQUIRED_SECTIONS = ["文獻名稱", "文獻中文名稱", "一句話核心"]
STUDY_SECTIONS = ["30秒看懂這篇論文", "先備知識", "重要名詞", "研究動機", "方法流程", "圖表導讀", "理解檢查", "延伸閱讀"]
NAV_ITEMS = [("overview", "Overview", "總覽"), ("prerequisites", "Prerequisites", "先備知識"), ("terms", "Key Terms", "重要名詞"), ("motivation", "Motivation", "研究動機"), ("method", "Method", "方法流程"), ("results", "Results", "圖表導讀"), ("quiz", "Quiz", "理解檢查")]


def ensure_directory_exists():
    os.makedirs(BASE_PATH, exist_ok=True)


def normalize_heading_name(text):
    text = re.sub(r"^[#\s]+", "", text.strip())
    text = re.sub(r"^[\W_]+|[\W_]+$", "", text, flags=re.UNICODE)
    text = re.sub(r"^[一二三四五六七八九十]+[、.．]\s*", "", text)
    return text.strip()


def split_sections(content):
    sections, current, buffer = {}, None, []
    for line in content.splitlines():
        match = re.match(r"^\s*#{2,4}\s+(.+?)\s*$", line)
        if match:
            if current:
                sections[current] = "\n".join(buffer).strip()
            current, buffer = normalize_heading_name(match.group(1)), []
        elif current:
            buffer.append(line)
    if current:
        sections[current] = "\n".join(buffer).strip()
    return sections


def first_line(text, default=""):
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return default


def extract_url(content):
    match = re.search(r"URL\s*[:：]?\s*(https?://[^\s)\]>]+)", content, flags=re.I)
    return match.group(1).strip() if match else "#"


def extract_archive_date(entry):
    match = re.search(r"(?:歸檔時間|歸檔日期)[:：]?\s*(\d{4}-\d{2}-\d{2})", entry)
    return match.group(1) if match else datetime.now().strftime("%Y-%m-%d")


def markdown_to_html(text):
    return markdown.markdown(text, extensions=["extra", "nl2br", "sane_lists"]) if text.strip() else ""


def split_entries(full_content):
    pattern = re.compile(r"(?=^\s*(?:#\s*歸檔時間[:：]?\s*\d{4}-\d{2}-\d{2}|#{2,4}\s*歸檔日期[:：]?\s*\d{4}-\d{2}-\d{2}))", re.M)
    return [part.strip() for part in pattern.split(full_content) if part.strip()]


def strip_known_headers(entry):
    body = entry
    for name in REQUIRED_SECTIONS:
        body = re.sub(rf"^\s*#{{2,4}}\s*{re.escape(name)}\s*\n.*?(?=^\s*#{{2,4}}\s+|\Z)", "", body, flags=re.S | re.M)
    body = re.sub(r"^.*URL\s*[:：]?\s*https?://[^\n]+\n?", "", body, flags=re.M | re.I)
    body = re.sub(r"^\s*-\s*抓取時間[:：].*$", "", body, flags=re.M)
    body = re.sub(r"^\s*#*\s*(歸檔時間|歸檔日期)[:：].*$", "", body, flags=re.M)
    return body.strip()


def validate_and_fix_format(content):
    missing = [name for name in REQUIRED_SECTIONS if not re.search(rf"^\s*#{{2,4}}\s*{re.escape(name)}\s*$", content, flags=re.M)]
    if not missing:
        return True, content
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if len(lines) < 3:
        return False, content
    fixed_content = content
    if "文獻名稱" in missing and "文獻中文名稱" in missing:
        start_idx = 1 if lines[0].startswith("# 歸檔時間") else 0
        fixed_content = f"### 文獻名稱\n{lines[start_idx]}\n\n### 文獻中文名稱\n{lines[start_idx + 1]}\n\n" + "\n".join(lines[start_idx + 2:])
    if "一句話核心" not in fixed_content:
        fixed_content = fixed_content.replace("\n\n", "\n\n### 一句話核心\n尚未填寫核心摘要\n\n", 1)
    return True, fixed_content


def parse_quiz(text):
    quiz = {"question": "", "options": [], "answer": "", "explanation": ""}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        q_match = re.match(r"^Q[:：]\s*(.+)$", line, flags=re.I)
        opt_match = re.match(r"^([A-D])\.\s*(.+)$", line)
        ans_match = re.match(r"^答案[:：]\s*([A-D]).*$", line)
        exp_match = re.match(r"^解釋[:：]\s*(.+)$", line)
        if q_match:
            quiz["question"] = q_match.group(1).strip()
        elif opt_match:
            quiz["options"].append((opt_match.group(1), opt_match.group(2).strip()))
        elif ans_match:
            quiz["answer"] = ans_match.group(1)
        elif exp_match:
            quiz["explanation"] = exp_match.group(1).strip()
    return quiz


def parse_paper(entry):
    sections = split_sections(entry)
    return {
        "raw": entry,
        "sections": sections,
        "is_study": any(name in sections for name in STUDY_SECTIONS),
        "eng_title": first_line(sections.get("文獻名稱", ""), "RESEARCH PAPER"),
        "chi_title": first_line(sections.get("文獻中文名稱", ""), "未命名研究"),
        "core": first_line(sections.get("一句話核心", ""), "點擊查看詳情"),
        "url": extract_url(entry),
        "date": extract_archive_date(entry),
    }


def card_icon(card_id):
    return {"overview": "◎", "prerequisites": "□", "terms": "◇", "motivation": "※", "method": "→", "results": "▣", "quiz": "?", "reading": "+", "legacy": "¶"}.get(card_id, "•")


def render_markdown_card(card_id, title, body, extra_class=""):
    body = body.strip() or "論文未明確說明。"
    return f'''
      <section class="study-card {extra_class}" id="{html.escape(card_id)}">
        <div class="card-heading"><span class="card-icon">{card_icon(card_id)}</span><h2>{html.escape(title)}</h2></div>
        <div class="markdown-body">{markdown_to_html(body)}</div>
      </section>'''


def render_quiz_card(text):
    quiz = parse_quiz(text)
    if not quiz["question"] or not quiz["options"]:
        return render_markdown_card("quiz", "理解檢查", text)
    options = ""
    for key, label in quiz["options"]:
        options += f'<button class="quiz-option" type="button" data-option="{html.escape(key)}"><span>{html.escape(key)}</span>{html.escape(label)}</button>'
    return f'''
      <section class="study-card quiz-card" id="quiz" data-answer="{html.escape(quiz["answer"])}" data-explanation="{html.escape(quiz["explanation"] or "答題後再回來對照這篇論文的核心問題。")}">
        <div class="card-heading"><span class="card-icon">?</span><h2>理解檢查</h2></div>
        <p class="quiz-question">{html.escape(quiz["question"])}</p>
        <div class="quiz-options">{options}</div>
        <p class="quiz-feedback" aria-live="polite"></p>
      </section>'''


def render_method_flow(body):
    lines = []
    for line in body.splitlines():
        match = re.match(r"^\s*(?:\d+[.、]|[-*])\s*(.+)$", line)
        if match:
            lines.append(match.group(1).strip())
    if len(lines) < 2:
        return render_markdown_card("method", "方法流程", body)
    steps = ""
    for idx, line in enumerate(lines[:6], 1):
        if "：" in line:
            name, desc = line.split("：", 1)
        elif ":" in line:
            name, desc = line.split(":", 1)
        else:
            name, desc = f"步驟 {idx}", line
        steps += f'<div class="flow-step"><span class="flow-number">{idx}</span><strong>{html.escape(name.strip())}</strong><p>{html.escape(desc.strip())}</p></div>'
    return f'<section class="study-card flow-card" id="method"><div class="card-heading"><span class="card-icon">→</span><h2>方法流程</h2></div><div class="flow-line">{steps}</div></section>'


def scoped_card_ids(cards_html, index):
    for card_id in ["overview", "prerequisites", "terms", "motivation", "method", "results", "quiz", "reading", "legacy"]:
        cards_html = cards_html.replace(f'id="{card_id}"', f'id="paper-{index}-{card_id}"', 1)
    return cards_html


def render_study_article(paper, index):
    s = paper["sections"]
    date_tag = paper["date"][5:].replace("-", "/") if paper["date"] else datetime.now().strftime("%m/%d")
    fallback_quiz = "Q: 這篇論文最主要的貢獻是什麼？\nA. 論文未明確說明\nB. " + paper["core"] + "\nC. 論文未明確說明\nD. 論文未明確說明\n答案: B\n解釋: 這正是本文的一句話核心。"
    cards = [
        render_markdown_card("overview", "30 秒看懂這篇論文", s.get("30秒看懂這篇論文", paper["core"]), "overview-card"),
        render_markdown_card("prerequisites", "先備知識", s.get("先備知識", "")),
        render_markdown_card("terms", "重要名詞", s.get("重要名詞", "")),
        render_markdown_card("motivation", "研究動機", s.get("研究動機", "")),
        render_method_flow(s.get("方法流程", s.get("他們做了什麼？（研究方法）", ""))),
        render_markdown_card("results", "圖表導讀", s.get("圖表導讀", s.get("驚人發現與具體數據（關鍵結果）", ""))),
        render_quiz_card(s.get("理解檢查", fallback_quiz)),
        render_markdown_card("reading", "延伸閱讀", s.get("延伸閱讀", "論文未明確說明。")),
    ]
    nav = "".join(f'<a href="#paper-{index}-{target}"><span>{i}</span><strong>{eng}</strong><em>{zh}</em></a>' for i, (target, eng, zh) in enumerate(NAV_ITEMS, 1))
    cards_html = scoped_card_ids("".join(cards), index)
    return f'''
    <article class="paper-page" id="paper-{index}">
      <main class="paper-main">
        <header class="paper-hero">
          <div><p class="date-tag">[ {html.escape(date_tag)} ]</p><h1>{html.escape(paper["chi_title"])}</h1><p class="eng-title">{html.escape(paper["eng_title"])}</p></div>
          <div class="hero-actions"><a class="outline-btn" href="{html.escape(paper["url"])}" target="_blank" rel="noopener">閱讀原始論文</a><button class="study-toggle" type="button">進入 Study Mode</button></div>
          <div class="core-line"><span>CORE</span><p>{html.escape(paper["core"])}</p></div>
        </header>
        <div class="card-grid">{cards_html}</div>
      </main>
      <aside class="study-rail"><h2>學習導覽</h2><p>本篇學習路徑</p><nav>{nav}</nav><div class="hint-box"><strong>學習小提示</strong><p>先看 30 秒總覽，再進入方法與測驗，學習效果更穩。</p></div></aside>
    </article>'''


def render_legacy_article(paper, index):
    date_tag = paper["date"][5:].replace("-", "/") if paper["date"] else datetime.now().strftime("%m/%d")
    cards_html = scoped_card_ids(render_markdown_card("legacy", "摘要內容", strip_known_headers(paper["raw"])), index)
    return f'''
    <article class="paper-page legacy-page" id="paper-{index}">
      <main class="paper-main">
        <header class="paper-hero">
          <div><p class="date-tag">[ {html.escape(date_tag)} ]</p><h1>{html.escape(paper["chi_title"])}</h1><p class="eng-title">{html.escape(paper["eng_title"])}</p></div>
          <div class="hero-actions"><a class="outline-btn" href="{html.escape(paper["url"])}" target="_blank" rel="noopener">閱讀原始論文</a></div>
          <div class="core-line"><span>CORE</span><p>{html.escape(paper["core"])}</p></div>
        </header>
        <div class="card-grid single-column">{cards_html}</div>
      </main>
      <aside class="study-rail"><h2>學習導覽</h2><p>舊版摘要格式</p><div class="hint-box"><strong>提示</strong><p>這篇是舊格式資料，已用 fallback 模式顯示。</p></div></aside>
    </article>'''


def page_style():
    return r'''
:root{--bg:#f7f7f5;--paper:#fff;--ink:#111;--muted:#6f6f6f;--line:#deded8;--accent:#e92727;--soft:#f1f1ee;--sans:'Noto Sans TC',sans-serif;--serif:'Noto Serif TC',serif}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans)}a{color:inherit}.paper-page{display:grid;grid-template-columns:minmax(0,1fr)270px;gap:28px;min-height:100vh;padding:32px 28px 28px 46px;border-bottom:1px solid var(--line)}.paper-main{min-width:0}.paper-hero{display:grid;grid-template-columns:minmax(0,1fr)auto;gap:18px 28px;align-items:start;margin-bottom:18px}.date-tag{margin:0 0 4px;font-size:16px;font-weight:700}h1{font-family:var(--serif);font-size:clamp(38px,5vw,72px);line-height:1.06;margin:0;letter-spacing:0}.eng-title{margin:8px 0 0;color:#949494;text-transform:uppercase;letter-spacing:2px;font-size:16px}.hero-actions{display:flex;gap:14px;align-items:center;padding-top:38px}.outline-btn,.study-toggle{min-height:56px;border-radius:6px;padding:0 28px;display:inline-flex;align-items:center;justify-content:center;font-size:16px;font-weight:800;text-decoration:none;border:2px solid var(--ink);background:var(--paper);cursor:pointer;white-space:nowrap}.study-toggle{background:var(--ink);color:#fff}.core-line{grid-column:1/-1;display:flex;gap:14px;align-items:flex-start;font-size:17px;line-height:1.75}.core-line span{background:var(--ink);color:#fff;font-size:12px;padding:3px 10px;font-weight:900;letter-spacing:1px;margin-top:6px}.core-line p{margin:0}.card-grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:12px}.study-card{background:rgba(255,255,255,.72);border:1px solid var(--line);border-radius:7px;padding:20px 22px;min-height:150px;scroll-margin-top:24px}.study-card:nth-child(1),.study-card:nth-child(4),.study-card:nth-child(5),.study-card:nth-child(6){grid-column:span 6}.study-card:nth-child(2),.study-card:nth-child(3),.study-card:nth-child(7),.study-card:nth-child(8){grid-column:span 4}.single-column .study-card{grid-column:1/-1}.card-heading{display:flex;align-items:center;gap:12px;margin-bottom:12px}.card-icon{color:var(--accent);border:1px solid var(--accent);width:24px;height:24px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-weight:900;flex:0 0 auto}.card-heading h2{margin:0;font-size:20px;line-height:1.2}.markdown-body{font-size:15px;line-height:1.75}.markdown-body p{margin:0 0 10px}.markdown-body ul,.markdown-body ol{margin:0;padding-left:20px}.markdown-body li{margin:7px 0}.markdown-body strong{font-weight:900}.flow-card{grid-column:span 8!important}.flow-line{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:12px}.flow-step{background:var(--soft);border:1px solid var(--line);border-radius:6px;padding:14px;min-height:130px}.flow-number{display:inline-flex;width:26px;height:26px;border-radius:50%;background:var(--ink);color:#fff;align-items:center;justify-content:center;font-size:13px;font-weight:900;margin-bottom:10px}.flow-step strong{display:block;margin-bottom:8px}.flow-step p{margin:0;color:#444;font-size:13px;line-height:1.6}.quiz-question{font-weight:800;margin-top:0}.quiz-options{display:grid;gap:8px}.quiz-option{width:100%;border:1px solid var(--line);background:#fff;border-radius:7px;padding:10px 12px;text-align:left;cursor:pointer;font:inherit;display:flex;gap:10px;align-items:flex-start}.quiz-option span{color:var(--muted);font-weight:900}.quiz-option.correct{border-color:var(--accent);background:#fff4f4}.quiz-option.wrong{opacity:.55}.quiz-feedback{margin:10px 0 0;color:var(--accent);font-weight:800}.study-rail{position:sticky;top:0;height:100vh;padding:34px 0 28px 28px;border-left:1px solid var(--line);background:var(--bg)}.study-rail h2{margin:0 0 16px;font-size:22px}.study-rail>p{color:var(--muted);border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:20px}.study-rail nav{display:grid;gap:12px}.study-rail nav a{display:grid;grid-template-columns:34px 1fr;gap:8px 10px;text-decoration:none;align-items:start}.study-rail nav span{width:26px;height:26px;border-radius:50%;border:1px solid #c8c8c8;display:inline-flex;align-items:center;justify-content:center;color:#777;font-size:13px}.study-rail nav strong{font-size:15px}.study-rail nav em{grid-column:2;color:#444;font-style:normal;font-size:14px}.hint-box{margin-top:40px;border:1px solid var(--line);border-radius:7px;background:rgba(255,255,255,.6);padding:18px;line-height:1.8}.hint-box p{margin:10px 0 0;color:#666}body.study-mode .paper-page:not(.active-study){display:none}body.study-mode .study-card{opacity:.38;transition:opacity .2s,transform .2s}body.study-mode .study-card:hover,body.study-mode .study-card:target{opacity:1;transform:translateY(-2px)}body.study-mode .study-toggle{background:var(--accent);border-color:var(--accent)}@media(max-width:1080px){.paper-page{grid-template-columns:1fr;padding:24px}.study-rail{position:static;height:auto;border-left:0;border-top:1px solid var(--line);padding:20px 0 0}.study-rail nav{grid-template-columns:repeat(2,minmax(0,1fr))}.hero-actions{padding-top:0}}@media(max-width:760px){.paper-hero{grid-template-columns:1fr}.hero-actions{flex-wrap:wrap}.outline-btn,.study-toggle{width:100%}.study-card,.flow-card{grid-column:1/-1!important}.study-rail nav{grid-template-columns:1fr}.paper-page{padding:18px}h1{font-size:38px}}
'''


def page_script():
    return r'''
document.querySelectorAll('.study-toggle').forEach((button)=>{button.addEventListener('click',()=>{const page=button.closest('.paper-page');const active=document.body.classList.toggle('study-mode');document.querySelectorAll('.paper-page').forEach((item)=>item.classList.remove('active-study'));if(active){page.classList.add('active-study');button.textContent='離開 Study Mode'}else{document.querySelectorAll('.study-toggle').forEach((item)=>item.textContent='進入 Study Mode')}})});
document.querySelectorAll('.quiz-card').forEach((card)=>{const answer=card.dataset.answer;const explanation=card.dataset.explanation;const feedback=card.querySelector('.quiz-feedback');card.querySelectorAll('.quiz-option').forEach((option)=>{option.addEventListener('click',()=>{card.querySelectorAll('.quiz-option').forEach((item)=>{item.classList.toggle('correct',item.dataset.option===answer);item.classList.toggle('wrong',item.dataset.option!==answer)});feedback.textContent=option.dataset.option===answer?`答對了：${explanation}`:`再想一下：正確答案是 ${answer}。${explanation}`})})});
'''


def render_page(papers):
    articles = [render_study_article(paper, i) if paper["is_study"] else render_legacy_article(paper, i) for i, paper in enumerate(papers, 1)]
    return f'''<!DOCTYPE html><html lang="zh-TW"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Arxiv Study Mode</title><link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@700;900&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet"><style>{page_style()}</style></head><body><div class="site-shell">{''.join(articles)}</div><script>{page_script()}</script></body></html>'''


def git_push_auto():
    if os.environ.get("ARXIV_SKIP_GIT") == "1":
        print("[Git] ARXIV_SKIP_GIT=1，略過自動推送。")
        return
    try:
        os.chdir(REPO_PATH)
        if not os.path.exists(".git"):
            subprocess.run(["git", "init"], check=True)
        remote_check = subprocess.run(["git", "remote"], capture_output=True, text=True)
        if "origin" not in remote_check.stdout:
            subprocess.run(["git", "remote", "add", "origin", GITHUB_REMOTE_URL], check=True)
        else:
            subprocess.run(["git", "remote", "set-url", "origin", GITHUB_REMOTE_URL], check=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        commit_result = subprocess.run(["git", "commit", "-m", f"Auto-Update: {datetime.now().strftime('%m-%d %H:%M')}"], capture_output=True, text=True)
        commit_output = (commit_result.stdout + commit_result.stderr).lower()
        if commit_result.returncode != 0 and "nothing to commit" not in commit_output:
            print(f"[Git Error] commit 失敗: {commit_result.stderr.strip()}")
        result = subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)
        if result.returncode == 0:
            print("[Git] 同步至 GitHub 成功。")
        else:
            print(f"[Git Error] push 失敗: {result.stderr.strip()}")
    except Exception as e:
        print(f"[Git Error] 異常: {str(e)}")


def mode_render():
    if not os.path.exists(SUMMARY_FILE):
        print(f"[Render] 找不到總結文件: {SUMMARY_FILE}")
        return
    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        full_content = f.read()
    entries = [entry for entry in split_entries(full_content) if "文獻名稱" in entry or "文獻中文名稱" in entry]
    if not entries:
        print("[Render] 沒有可渲染的摘要。")
        return
    papers = [parse_paper(entry) for entry in reversed(entries)]
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(render_page(papers))
    print(f"[Render] {OUTPUT_HTML} 更新完成，共 {len(papers)} 篇。")
    git_push_auto()


def mode_merge():
    target_file = TEMP_RESULT if os.path.exists(TEMP_RESULT) else TEMP_TASK
    if not os.path.exists(target_file):
        print("[Merge] 找不到暫存檔。")
        return
    with open(target_file, "r", encoding="utf-8") as f:
        raw_content = f.read()
    success, final_content = validate_and_fix_format(raw_content)
    if not success:
        print("[Merge] 格式校驗失敗，保留暫存檔以便重跑。")
        return
    ensure_directory_exists()
    with open(SUMMARY_FILE, "a", encoding="utf-8") as sf:
        sf.write(f"\n\n# 歸檔時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        sf.write(final_content.strip() + "\n")
    for temp_file in [TEMP_TASK, TEMP_RESULT]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    mode_render()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["merge", "render"], required=True)
    args = parser.parse_args()
    if args.mode == "merge":
        mode_merge()
    elif args.mode == "render":
        mode_render()
