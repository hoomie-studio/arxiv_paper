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
ALLOWED_TAGS = [
    "reconstruction",
    "remote sensing",
    "point cloud",
    "object detection",
    "GIS",
    "digital twin",
    "Lidar",
    "machine learning",
    "photogrammetry",
]
TAG_LOOKUP = {tag.lower(): tag for tag in ALLOWED_TAGS}


def ensure_directory_exists():
    os.makedirs(BASE_PATH, exist_ok=True)


def md_to_html(text):
    return markdown.markdown(text.strip(), extensions=["extra", "nl2br", "sane_lists", "tables"]) if text.strip() else ""


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
    summary = extract_between(entry, SUMMARY_START, SUMMARY_END) or entry
    study = extract_between(entry, STUDY_START, STUDY_END)
    summary_sections = split_sections(summary)
    study_sections = split_sections(study)
    title = first_line(summary_sections.get("文獻中文名稱", study_sections.get("文獻中文名稱", "")), "未命名研究")
    eng_title = first_line(summary_sections.get("文獻名稱", study_sections.get("文獻名稱", "")), "RESEARCH PAPER")
    core = first_line(summary_sections.get("一句話核心", study_sections.get("一句話核心", "")), "點擊查看詳情")
    date_match = re.search(r"歸檔時間[:：]?\s*(\d{4}-\d{2}-\d{2})", entry)
    tags = parse_tags(summary_sections.get("分類關鍵字", "") + "\n" + study_sections.get("分類關鍵字", ""))
    return {
        "raw": entry,
        "summary": summary,
        "study": study,
        "summary_sections": summary_sections,
        "study_sections": study_sections,
        "title": title,
        "eng_title": eng_title,
        "core": core,
        "url": extract_url(summary + "\n" + study),
        "date": date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d"),
        "tags": tags,
    }


def parse_tags(text):
    found = []
    lowered = text.lower()
    for key, canonical in TAG_LOOKUP.items():
        if re.search(rf"(?<![a-z0-9]){re.escape(key)}(?![a-z0-9])", lowered):
            found.append(canonical)
    return found


def strip_meta_sections(sections, names):
    return "\n\n".join(f"### {name}\n{sections[name]}" for name in names if sections.get(name, "").strip())


def render_article(paper, idx):
    ss, ts = paper["summary_sections"], paper["study_sections"]
    date_tag = paper["date"][5:].replace("-", "/")
    tag_html = "".join(f'<span class="paper-tag">{html.escape(tag)}</span>' for tag in paper["tags"])
    data_tags = "|".join(paper["tags"])
    summary_body = strip_meta_sections(ss, [
        "秒懂表格",
        "為什麼要研究這個？（研究動機）",
        "他們做了什麼？（研究方法）",
        "驚人發現與具體數據（關鍵結果）",
        "這對我有什麼意義？（實際應用）",
    ]) or paper["summary"]
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
    cards = "".join(render_card(name, body) for name, body in study_cards if body.strip()) or render_card("Study Mode", paper["study"] or "尚未產生 Study Mode 內容。")
    return f'''
      <section class="swiper-slide paper-slide" data-tags="{html.escape(data_tags)}">
        <div class="hk-container">
          <div class="hk-background-text">SEARCH</div>
          <div class="hk-grid">
            <div class="hk-left-col">
              <p class="hk-tag">[ {html.escape(date_tag)} ]</p>
              <h1 class="hk-main-title">{html.escape(paper["title"])}</h1>
              <p class="hk-eng-subtitle">{html.escape(paper["eng_title"])}</p>
              <div class="hk-core-statement"><span class="hk-label">CORE</span><p>{html.escape(paper["core"])}</p></div>
              <div class="paper-tags">{tag_html}</div>
              <div class="hero-actions">
                <a class="hk-link-btn" href="{html.escape(paper["url"])}" target="_blank" rel="noopener">閱讀原始論文</a>
                <button class="hk-link-btn dark" type="button" data-open-study>進入 Study Mode</button>
              </div>
            </div>
            <div class="hk-right-col">
              <section class="summary-panel">
                <div class="mode-eyebrow">Summary</div>
                <h2>這篇研究在做什麼？</h2>
                <div class="markdown-body">{md_to_html(summary_body)}</div>
              </section>
              <section class="study-panel" hidden>
                <div class="study-head"><div><div class="mode-eyebrow">Study Mode</div><h2>學習導覽</h2></div><button class="mini-btn" type="button" data-close-study>回到 Summary</button></div>
                <div class="card-grid">{cards}</div>
              </section>
            </div>
          </div>
          <div class="hk-footer"><div class="hk-logo">HUMANKIND <span>×</span> GEOMATICS</div><div class="hk-scroll-hint">SWIPE RIGHT —</div></div>
        </div>
      </section>'''


def render_card(title, body):
    return f'<section class="card"><h3>{html.escape(title)}</h3><div class="markdown-body">{md_to_html(body)}</div></section>'


def render_page(papers):
    filters = "".join(f'<button type="button" data-filter="{html.escape(tag)}">{html.escape(tag)}</button>' for tag in ALLOWED_TAGS)
    slides = "".join(render_article(p, i) for i, p in enumerate(papers, 1))
    return f'''<!DOCTYPE html><html lang="zh-TW"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Arxiv Paper Study Library</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css"/><link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@700;900&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet"><style>{page_style()}</style></head><body><nav class="filterbar"><strong>Arxiv Paper Library</strong><div class="filters"><button type="button" data-filter="__all" class="active">全部</button>{filters}</div></nav><div class="swiper"><div class="swiper-wrapper">{slides}</div></div><script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script><script>{page_script()}</script></body></html>'''


def page_style():
    return r'''
:root{--hk-bg:#f8f8f8;--hk-black:#0a0a0a;--hk-red:#e63946;--hk-gray:#e0e0e0;--soft:#f1f1ee;--serif:'Noto Serif TC',serif;--sans:'Noto Sans TC',sans-serif}*{box-sizing:border-box;margin:0;padding:0}body,html{height:100%;overflow:hidden;background:var(--hk-bg);color:var(--hk-black);font-family:var(--sans)}.filterbar{position:fixed;left:0;right:0;top:0;z-index:10;height:54px;display:flex;align-items:center;justify-content:space-between;gap:18px;padding:0 34px;border-bottom:1px solid var(--hk-gray);background:rgba(248,248,248,.94);backdrop-filter:blur(8px)}.filterbar strong{font-weight:900;letter-spacing:1px}.filters{display:flex;gap:8px;overflow:auto}.filters button,.mini-btn{border:1px solid var(--hk-black);background:#fff;border-radius:5px;padding:7px 10px;font:inherit;font-size:12px;font-weight:800;white-space:nowrap;cursor:pointer}.filters button.active{background:var(--hk-black);color:#fff}.swiper{width:100%;height:100vh;padding-top:54px}.hk-container{width:100%;height:calc(100vh - 54px);padding:48px 60px 34px;display:flex;flex-direction:column;position:relative;z-index:1}.hk-background-text{position:absolute;top:4%;right:5%;font-size:20vw;font-weight:900;color:rgba(0,0,0,.035);z-index:0;pointer-events:none;white-space:nowrap}.hk-grid{display:grid;grid-template-columns:1.05fr 1fr;gap:64px;z-index:1;flex-grow:1;min-height:0;margin-bottom:24px}.hk-left-col{min-width:0}.hk-right-col{position:relative;overflow-y:auto;padding-right:20px;scrollbar-width:thin;scrollbar-color:var(--hk-black) transparent}.hk-tag{font-weight:800;margin-bottom:8px}.hk-main-title{font-family:var(--serif);font-size:clamp(2.1rem,4.8vw,5.2rem);line-height:1.08;font-weight:900;letter-spacing:0;margin-bottom:12px}.hk-eng-subtitle{font-size:.88rem;color:#888;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:28px}.hk-core-statement{display:flex;gap:18px;align-items:flex-start;margin-bottom:18px}.hk-label{background:var(--hk-black);color:#fff;padding:4px 10px;font-size:.7rem;font-weight:900;transform:rotate(-90deg) translateX(-5px);margin-top:16px}.hk-core-statement p{font-size:1.22rem;font-family:var(--serif);line-height:1.45;font-weight:800}.paper-tags{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0}.paper-tag{background:#fff;border:1px solid var(--hk-gray);border-radius:999px;padding:7px 10px;font-size:12px;font-weight:900;color:#333}.hero-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:20px}.hk-link-btn{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:0 18px;border:2px solid var(--hk-black);border-radius:5px;color:var(--hk-black);text-decoration:none;font-weight:900;background:#fff;cursor:pointer;font:inherit}.hk-link-btn.dark{background:var(--hk-black);color:#fff}.summary-panel,.study-panel{background:rgba(255,255,255,.76);border:1px solid var(--hk-gray);border-radius:7px;padding:22px}.mode-eyebrow{color:var(--hk-red);font-weight:900;text-transform:uppercase;letter-spacing:1px;font-size:12px}.summary-panel h2,.study-head h2{font-size:24px;margin:4px 0 14px}.markdown-body{font-size:16px;line-height:1.78}.markdown-body h3{font-family:var(--serif);font-size:1.35rem;margin:24px 0 10px;border-bottom:2px solid var(--hk-black);display:inline-block}.markdown-body p{margin-bottom:14px;text-align:justify}.markdown-body strong,.markdown-body b{color:var(--hk-red);font-weight:900}.markdown-body ul,.markdown-body ol{padding-left:20px;margin-bottom:12px}.markdown-body li{padding:7px 0;line-height:1.65}.markdown-body table{width:100%;border-collapse:separate;border-spacing:0;margin:8px 0 18px;border:1px solid var(--hk-gray);border-radius:7px;overflow:hidden;background:#fff}.markdown-body th{background:var(--hk-black);color:#fff;text-align:left;padding:10px}.markdown-body td{border-top:1px solid var(--hk-gray);padding:12px;vertical-align:top}.markdown-body td:first-child{width:34%;font-weight:900;color:var(--hk-red)}.study-head{display:flex;justify-content:space-between;gap:12px;align-items:start;margin-bottom:14px}.card-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.card{background:#fff;border:1px solid var(--hk-gray);border-radius:7px;padding:16px}.card h3{font-size:18px;color:var(--hk-red);margin-bottom:10px}.hk-footer{flex-shrink:0;display:flex;justify-content:space-between;align-items:flex-end;border-top:1px solid #000;padding-top:16px;z-index:2;background:var(--hk-bg)}.hk-logo{font-weight:900;letter-spacing:2px}.hk-logo span{color:var(--hk-red)}.hk-scroll-hint{font-size:.78rem;letter-spacing:3px;font-weight:800}.paper-slide.hidden{display:none!important}@media(max-width:980px){body,html{overflow:auto}.filterbar{position:sticky;height:auto;display:block;padding:12px 18px}.filters{margin-top:10px}.swiper{height:auto;padding-top:0}.hk-container{height:auto;min-height:100vh;padding:24px 18px}.hk-grid{grid-template-columns:1fr;gap:24px}.hk-main-title{font-size:2.4rem}.card-grid{grid-template-columns:1fr}.hk-footer{display:none}.hk-right-col{overflow:visible;padding-right:0}}'''


def page_script():
    return r'''
const swiper=new Swiper('.swiper',{speed:700,mousewheel:{forceToAxis:true},keyboard:{enabled:true},direction:'horizontal'});
document.querySelectorAll('[data-open-study]').forEach(btn=>btn.addEventListener('click',()=>{const slide=btn.closest('.paper-slide');slide.querySelector('.summary-panel').hidden=true;slide.querySelector('.study-panel').hidden=false;}));
document.querySelectorAll('[data-close-study]').forEach(btn=>btn.addEventListener('click',()=>{const slide=btn.closest('.paper-slide');slide.querySelector('.study-panel').hidden=true;slide.querySelector('.summary-panel').hidden=false;}));
document.querySelectorAll('[data-filter]').forEach(btn=>btn.addEventListener('click',()=>{const tag=btn.dataset.filter;document.querySelectorAll('[data-filter]').forEach(b=>b.classList.toggle('active',b===btn));document.querySelectorAll('.paper-slide').forEach(slide=>{slide.classList.toggle('hidden',tag!=='__all'&&!slide.dataset.tags.split('|').includes(tag));});swiper.update();swiper.slideTo(0,0);}));
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