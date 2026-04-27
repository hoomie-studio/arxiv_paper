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
HISTORY_FILE = os.path.join(BASE_PATH, "arxiv_history.md")
TEMP_TASK = os.path.join(BASE_PATH, "temp_task.md")
TEMP_SUMMARY = os.path.join(BASE_PATH, "temp_summary.md")
TEMP_STUDYMODE = os.path.join(BASE_PATH, "temp_studymode.md")
TEMP_RESULT = os.path.join(BASE_PATH, "temp_result.md")
LIBRARY_FILE = os.path.join(BASE_PATH, "paper_summary.md")
GITHUB_REMOTE_URL = "https://github.com/hoomie-studio/arxiv_paper.git"

SUMMARY_START = "<!-- SUMMARY_START -->"
SUMMARY_END = "<!-- SUMMARY_END -->"
STUDY_START = "<!-- STUDYMODE_START -->"
STUDY_END = "<!-- STUDYMODE_END -->"
REQUIRED_SECTIONS = ["文獻名稱", "文獻中文名稱", "一句話核心"]


def ensure_directory_exists():
    os.makedirs(BASE_PATH, exist_ok=True)


def md_to_html(text):
    return markdown.markdown(text.strip(), extensions=["extra", "nl2br", "sane_lists"]) if text.strip() else ""


def normalize_heading(text):
    text = re.sub(r"^[#\s]+", "", text.strip())
    return re.sub(r"^[\W_]+|[\W_]+$", "", text, flags=re.UNICODE).strip()


def split_sections(content):
    sections, current, buf = {}, None, []
    for line in content.splitlines():
        m = re.match(r"^\s*#{2,4}\s+(.+?)\s*$", line)
        if m:
            if current:
                sections[current] = "\n".join(buf).strip()
            current, buf = normalize_heading(m.group(1)), []
        elif current:
            buf.append(line)
    if current:
        sections[current] = "\n".join(buf).strip()
    return sections


def first_line(text, default=""):
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return default


def extract_url(text):
    m = re.search(r"URL\s*[:：]?\s*(https?://[^\s)\]>]+)", text, flags=re.I)
    return m.group(1).strip() if m else "#"


def validate_output(content, label):
    missing = [name for name in REQUIRED_SECTIONS if not re.search(rf"^\s*#{{2,4}}\s*{re.escape(name)}\s*$", content, flags=re.M)]
    if missing:
        print(f"[Merge] {label} 缺少必要標題: {', '.join(missing)}")
        return False
    return True


def extract_between(text, start, end):
    if start not in text:
        return ""
    after = text.split(start, 1)[1]
    return after.split(end, 1)[0].strip() if end in after else after.strip()


def split_entries(full_content):
    pattern = re.compile(r"(?=^\s*#\s*歸檔時間[:：]?\s*\d{4}-\d{2}-\d{2})", re.M)
    return [part.strip() for part in pattern.split(full_content) if part.strip()]


def parse_entry(entry):
    summary = extract_between(entry, SUMMARY_START, SUMMARY_END)
    study = extract_between(entry, STUDY_START, STUDY_END)
    if not summary:
        summary = entry
    summary_sections = split_sections(summary)
    study_sections = split_sections(study)
    merged = {**summary_sections, **{f"study:{k}": v for k, v in study_sections.items()}}
    title = first_line(summary_sections.get("文獻中文名稱", study_sections.get("文獻中文名稱", "")), "未命名研究")
    eng_title = first_line(summary_sections.get("文獻名稱", study_sections.get("文獻名稱", "")), "RESEARCH PAPER")
    core = first_line(summary_sections.get("一句話核心", study_sections.get("一句話核心", "")), "點擊查看詳情")
    date_match = re.search(r"歸檔時間[:：]?\s*(\d{4}-\d{2}-\d{2})", entry)
    return {
        "raw": entry,
        "summary": summary,
        "study": study,
        "summary_sections": summary_sections,
        "study_sections": study_sections,
        "sections": merged,
        "title": title,
        "eng_title": eng_title,
        "core": core,
        "url": extract_url(summary + "\n" + study),
        "date": date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d"),
        "tags": parse_tags(summary_sections.get("分類關鍵字", "") + "\n" + study_sections.get("分類關鍵字", "")),
    }


def parse_tags(text):
    tags = []
    for line in text.splitlines():
        line = re.sub(r"^\s*[-*]\s*", "", line.strip())
        if not line or "：" not in line and ":" not in line:
            continue
        key, val = re.split(r"[:：]", line, 1)
        key, val = key.strip(), val.strip().strip("[]")
        if key in ["主題類別", "方法類別", "任務類別", "難度"] and val:
            tags.append(val)
        elif key == "關鍵字":
            tags.extend([x.strip() for x in re.split(r"[,，、]", val) if x.strip()])
    seen, out = set(), []
    for tag in tags:
        if tag and tag not in seen and "例如" not in tag:
            seen.add(tag)
            out.append(tag)
    return out[:10]


def strip_meta_sections(sections, names):
    return "\n\n".join(f"### {name}\n{sections[name]}" for name in names if sections.get(name, "").strip())


def render_article(paper, idx):
    ss, ts = paper["summary_sections"], paper["study_sections"]
    date_tag = paper["date"][5:].replace("-", "/")
    tags = "".join(f'<span class="tag" data-tag="{html.escape(t)}">{html.escape(t)}</span>' for t in paper["tags"])
    data_tags = "|".join(paper["tags"])
    summary_body = strip_meta_sections(ss, ["為什麼要研究這個？（研究動機）", "他們做了什麼？（研究方法）", "驚人發現與具體數據（關鍵結果）", "這對我有什麼意義？（實際應用）"])
    if not summary_body:
        summary_body = paper["summary"]
    study_cards = [
        ("學習路徑", ts.get("學習路徑", "")),
        ("先備知識", ts.get("先備知識", "")),
        ("重要名詞", ts.get("重要名詞", "")),
        ("脈絡梳理", ts.get("脈絡梳理", "")),
        ("方法流程", ts.get("方法流程", "")),
        ("圖表導讀", ts.get("圖表導讀", "")),
        ("觀念確認", ts.get("觀念確認", "")),
        ("理解檢查", ts.get("理解檢查", "")),
        ("延伸閱讀", ts.get("延伸閱讀", "")),
    ]
    cards = "".join(render_card(name, body) for name, body in study_cards if body.strip())
    if not cards:
        cards = render_card("Study Mode", paper["study"] or "尚未產生 Study Mode 內容。")
    return f'''
    <article class="paper" data-tags="{html.escape(data_tags)}">
      <header class="hero">
        <div>
          <p class="date">[ {html.escape(date_tag)} ]</p>
          <h1>{html.escape(paper["title"])}</h1>
          <p class="eng">{html.escape(paper["eng_title"])}</p>
        </div>
        <div class="actions">
          <a class="btn secondary" href="{html.escape(paper["url"])}" target="_blank" rel="noopener">閱讀原始論文</a>
          <button class="btn primary" type="button" data-open-study>進入 Study Mode</button>
        </div>
        <div class="core"><span>CORE</span><p>{html.escape(paper["core"])}</p></div>
        <div class="tags">{tags}</div>
      </header>
      <section class="summary-panel">
        <div class="section-title"><span>Summary</span><h2>這篇研究在做什麼？</h2></div>
        <div class="markdown-body">{md_to_html(summary_body)}</div>
      </section>
      <section class="study-panel" hidden>
        <div class="study-head"><div><span>Study Mode</span><h2>學習導覽</h2></div><button class="btn secondary" type="button" data-close-study>回到 Summary</button></div>
        <div class="card-grid">{cards}</div>
      </section>
    </article>'''


def render_card(title, body):
    return f'<section class="card"><h3>{html.escape(title)}</h3><div class="markdown-body">{md_to_html(body)}</div></section>'


def render_page(papers):
    all_tags = []
    for p in papers:
        all_tags.extend(p["tags"])
    unique_tags = []
    for tag in all_tags:
        if tag not in unique_tags:
            unique_tags.append(tag)
    filters = "".join(f'<button type="button" data-filter="{html.escape(tag)}">{html.escape(tag)}</button>' for tag in unique_tags)
    articles = "".join(render_article(p, i) for i, p in enumerate(papers, 1))
    return f'''<!DOCTYPE html><html lang="zh-TW"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Arxiv Paper Study Library</title><link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@700;900&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet"><style>{page_style()}</style></head><body><nav class="topbar"><strong>Arxiv Paper Library</strong><div class="filters"><button type="button" data-filter="__all" class="active">全部</button>{filters}</div></nav><main>{articles}</main><script>{page_script()}</script></body></html>'''


def page_style():
    return r'''
:root{--bg:#f7f7f5;--paper:#fff;--ink:#111;--muted:#686868;--line:#ddd;--accent:#e92727;--soft:#f0f0ed;--sans:'Noto Sans TC',sans-serif;--serif:'Noto Serif TC',serif}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans)}.topbar{position:sticky;top:0;z-index:5;display:flex;gap:18px;align-items:center;justify-content:space-between;padding:14px 32px;border-bottom:1px solid var(--line);background:rgba(247,247,245,.94);backdrop-filter:blur(8px)}.filters{display:flex;gap:8px;overflow:auto}.filters button,.btn{border:1px solid var(--ink);border-radius:6px;background:#fff;padding:10px 14px;font:inherit;font-weight:800;cursor:pointer;text-decoration:none;color:var(--ink);white-space:nowrap}.filters button.active,.btn.primary{background:var(--ink);color:#fff}.paper{min-height:100vh;padding:36px 44px;border-bottom:1px solid var(--line)}.hero{display:grid;grid-template-columns:minmax(0,1fr)auto;gap:18px 28px;margin-bottom:18px}.date{margin:0 0 4px;font-weight:800}h1{font-family:var(--serif);font-size:clamp(36px,5vw,70px);line-height:1.08;margin:0}.eng{margin:8px 0 0;color:#8b8b8b;text-transform:uppercase;letter-spacing:2px}.actions{display:flex;gap:12px;align-items:start;padding-top:36px}.core{grid-column:1/-1;display:flex;gap:12px;font-size:17px;line-height:1.8}.core span{background:var(--ink);color:#fff;font-size:12px;padding:3px 10px;font-weight:900;height:max-content;margin-top:6px}.core p{margin:0}.tags{grid-column:1/-1;display:flex;gap:8px;flex-wrap:wrap}.tag{background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:6px 10px;font-size:13px;font-weight:800}.summary-panel,.study-panel{background:rgba(255,255,255,.7);border:1px solid var(--line);border-radius:8px;padding:24px}.section-title span,.study-head span{color:var(--accent);font-weight:900;text-transform:uppercase;font-size:12px;letter-spacing:1px}.section-title h2,.study-head h2{margin:4px 0 18px;font-size:26px}.markdown-body{font-size:16px;line-height:1.85}.markdown-body h3{font-size:20px;margin:22px 0 8px}.markdown-body p{margin:0 0 12px}.markdown-body li{margin:7px 0}.study-head{display:flex;justify-content:space-between;gap:16px;align-items:start;margin-bottom:16px}.card-grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:12px}.card{grid-column:span 4;background:#fff;border:1px solid var(--line);border-radius:7px;padding:18px}.card:nth-child(4),.card:nth-child(5),.card:nth-child(8){grid-column:span 6}.card h3{margin:0 0 10px;font-size:20px;color:var(--accent)}.paper.hidden{display:none}@media(max-width:980px){.topbar{display:block}.filters{margin-top:10px}.paper{padding:24px}.hero{grid-template-columns:1fr}.actions{padding-top:0;flex-wrap:wrap}.btn{width:100%;justify-content:center;display:inline-flex}.card{grid-column:1/-1!important}}'''


def page_script():
    return r'''
document.querySelectorAll('[data-open-study]').forEach(btn=>btn.addEventListener('click',()=>{const p=btn.closest('.paper');p.querySelector('.summary-panel').hidden=true;p.querySelector('.study-panel').hidden=false;p.scrollIntoView({behavior:'smooth',block:'start'});}));
document.querySelectorAll('[data-close-study]').forEach(btn=>btn.addEventListener('click',()=>{const p=btn.closest('.paper');p.querySelector('.study-panel').hidden=true;p.querySelector('.summary-panel').hidden=false;p.scrollIntoView({behavior:'smooth',block:'start'});}));
document.querySelectorAll('[data-filter]').forEach(btn=>btn.addEventListener('click',()=>{const tag=btn.dataset.filter;document.querySelectorAll('[data-filter]').forEach(b=>b.classList.toggle('active',b===btn));document.querySelectorAll('.paper').forEach(p=>{p.classList.toggle('hidden',tag!=='__all'&&!p.dataset.tags.split('|').includes(tag));});}));
'''


def update_history(summary_content):
    if not os.path.exists(HISTORY_FILE):
        return
    title = first_line(split_sections(summary_content).get("文獻名稱", ""), "")
    if not title:
        return
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = f.read()
    history = re.sub(rf"(##\s*{re.escape(title)}.*?狀態:\s*)\[PENDING\]", rf"\1[已完成摘要+StudyMode]", history, flags=re.S)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(history)


def git_push_auto():
    if os.environ.get("ARXIV_SKIP_GIT") == "1":
        print("[Git] ARXIV_SKIP_GIT=1，略過自動推送。")
        return
    try:
        os.chdir(REPO_PATH)
        if not os.path.exists(".git"):
            subprocess.run(["git", "init"], check=True)
        if "origin" not in subprocess.run(["git", "remote"], capture_output=True, text=True).stdout:
            subprocess.run(["git", "remote", "add", "origin", GITHUB_REMOTE_URL], check=True)
        else:
            subprocess.run(["git", "remote", "set-url", "origin", GITHUB_REMOTE_URL], check=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto-Update: {datetime.now().strftime('%m-%d %H:%M')}"], capture_output=True, text=True)
        result = subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)
        print("[Git] 同步至 GitHub 成功。" if result.returncode == 0 else f"[Git Error] push 失敗: {result.stderr.strip()}")
    except Exception as e:
        print(f"[Git Error] 異常: {e}")


def mode_merge():
    missing = [p for p in [TEMP_SUMMARY, TEMP_STUDYMODE] if not os.path.exists(p) or os.path.getsize(p) == 0]
    if missing:
        print("[Merge] Summary + Study Mode 尚未完整產生，不會合併。")
        for p in missing:
            print(f"- 缺少或為空: {p}")
        return
    with open(TEMP_SUMMARY, "r", encoding="utf-8") as f:
        summary = f.read().strip()
    with open(TEMP_STUDYMODE, "r", encoding="utf-8") as f:
        study = f.read().strip()
    if not validate_output(summary, "temp_summary.md") or not validate_output(study, "temp_studymode.md"):
        return
    ensure_directory_exists()
    with open(LIBRARY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n\n# 歸檔時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{SUMMARY_START}\n{summary}\n{SUMMARY_END}\n\n{STUDY_START}\n{study}\n{STUDY_END}\n")
    update_history(summary)
    for p in [TEMP_TASK, TEMP_SUMMARY, TEMP_STUDYMODE, TEMP_RESULT]:
        if os.path.exists(p):
            os.remove(p)
    mode_render()


def mode_render():
    if not os.path.exists(LIBRARY_FILE):
        print(f"[Render] 找不到資料庫: {LIBRARY_FILE}")
        return
    with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
        entries = split_entries(f.read())
    papers = [parse_entry(e) for e in reversed(entries) if "文獻名稱" in e or SUMMARY_START in e]
    if not papers:
        print("[Render] 沒有可渲染資料。")
        return
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(render_page(papers))
    print(f"[Render] {OUTPUT_HTML} 更新完成，共 {len(papers)} 篇。")
    git_push_auto()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["merge", "render"], required=True)
    args = parser.parse_args()
    if args.mode == "merge":
        mode_merge()
    else:
        mode_render()