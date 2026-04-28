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
    "reconstruction", "remote sensing", "point cloud", "object detection", "GIS",
    "digital twin", "Lidar", "machine learning", "photogrammetry",
]
TAG_LOOKUP = {tag.lower(): tag for tag in ALLOWED_TAGS}


def ensure_directory_exists():
    os.makedirs(BASE_PATH, exist_ok=True)


def md_to_html(text):
    text = (text or "").strip()
    if not text:
        return ""
    return markdown.markdown(text, extensions=["extra", "nl2br", "sane_lists", "tables"])


def normalize_heading(text):
    text = re.sub(r"^[#\s]+", "", text.strip())
    return re.sub(r"^[\W_]+|[\W_]+$", "", text, flags=re.UNICODE).strip()


def split_sections(content):
    sections, current, buf = {}, None, []
    for line in (content or "").splitlines():
        m = re.match(r"^\s*#{2,5}\s+(.+?)\s*$", line)
        if m:
            if current:
                sections[current] = "\n".join(buf).strip()
            current, buf = normalize_heading(m.group(1)), []
        elif current:
            buf.append(line)
    if current:
        sections[current] = "\n".join(buf).strip()
    return sections


def get_section(sections, *names):
    for name in names:
        if sections.get(name, "").strip():
            return sections[name].strip()
    return ""


def first_line(text, default=""):
    for line in (text or "").splitlines():
        clean = re.sub(r"^[\-*\s]+", "", line).strip()
        if clean:
            return clean
    return default


def extract_url(text):
    m = re.search(r"URL\s*[:：]?\s*\[?\s*(https?://[^\s)\]>]+)", text or "", flags=re.I)
    return m.group(1).strip() if m else "#"


def validate_output(content, label):
    missing = [
        name for name in REQUIRED_SECTIONS
        if not re.search(rf"^\s*#{{2,5}}\s*{re.escape(name)}\s*$", content or "", flags=re.M)
    ]
    if missing:
        print(f"[Merge] {label} 缺少必要章節: {', '.join(missing)}")
        return False
    return True


def extract_between(text, start, end):
    if start not in text:
        return ""
    after = text.split(start, 1)[1]
    return after.split(end, 1)[0].strip() if end in after else after.strip()


def split_entries(full_content):
    pattern = re.compile(r"(?=^\s*#\s*(?:歸檔時間|歸檔日期)\s*[:：]?\s*\d{4}-\d{2}-\d{2})", re.M)
    return [part.strip() for part in pattern.split(full_content or "") if part.strip()]


def parse_tags(text):
    found = []
    lowered = (text or "").lower()
    for key, canonical in TAG_LOOKUP.items():
        if re.search(rf"(?<![a-z0-9]){re.escape(key)}(?![a-z0-9])", lowered):
            found.append(canonical)
    return found


def parse_entry(entry):
    summary = extract_between(entry, SUMMARY_START, SUMMARY_END) or entry
    study = extract_between(entry, STUDY_START, STUDY_END)
    summary_sections = split_sections(summary)
    study_sections = split_sections(study)
    title = first_line(get_section(summary_sections, "文獻中文名稱") or get_section(study_sections, "文獻中文名稱"), "未命名論文")
    eng_title = first_line(get_section(summary_sections, "文獻名稱") or get_section(study_sections, "文獻名稱"), "RESEARCH PAPER")
    core = first_line(get_section(summary_sections, "一句話核心") or get_section(study_sections, "一句話核心"), "尚未提供核心摘要")
    date_match = re.search(r"(?:歸檔時間|歸檔日期)\s*[:：]?\s*(\d{4}-\d{2}-\d{2})", entry)
    tag_source = get_section(summary_sections, "分類關鍵字") + "\n" + get_section(study_sections, "分類關鍵字")
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
        "tags": parse_tags(tag_source),
    }


def strip_meta_sections(sections, names):
    parts = []
    for name in names:
        body = get_section(sections, name)
        if body:
            parts.append(f"### {name}\n{body}")
    return "\n\n".join(parts)


def parse_quizzes(text):
    quizzes = []
    pattern = re.compile(
        r"Q(?P<num>\d+)\s*[:：]\s*(?P<question>.*?)\n"
        r"A\.\s*(?P<A>.*?)\n"
        r"B\.\s*(?P<B>.*?)\n"
        r"C\.\s*(?P<C>.*?)\n"
        r"D\.\s*(?P<D>.*?)\n"
        r"答案\s*[:：]\s*(?P<answer>[ABCD])\s*\n"
        r"解釋\s*[:：]\s*(?P<explanation>.*?)(?=\n\s*Q\d+\s*[:：]|\Z)",
        flags=re.S | re.I,
    )
    for match in pattern.finditer(text or ""):
        quizzes.append({
            "num": match.group("num"),
            "question": match.group("question").strip(),
            "options": {key: match.group(key).strip() for key in "ABCD"},
            "answer": match.group("answer").upper(),
            "explanation": match.group("explanation").strip(),
        })
    return quizzes


def quick_excerpt(text, max_items=3):
    lines = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("Q1:", "Q2:", "Q3:", "A.", "B.", "C.", "D.", "答案", "解釋")):
            continue
        line = re.sub(r"^[-*]\s*", "- ", line)
        lines.append(line)
        if len(lines) >= max_items:
            break
    return "\n".join(lines) if lines else (text or "").strip()


def render_card(title, body, card_id=""):
    anchor = f' id="{html.escape(card_id)}"' if card_id else ""
    quick = quick_excerpt(body)
    detail_id = f"{card_id}-detail" if card_id else ""
    detail_attr = f' id="{html.escape(detail_id)}"' if detail_id else ""
    return (
        f'<section class="study-card"{anchor}>'
        f'<div class="card-kicker">快速版</div>'
        f'<h3>{html.escape(title)}</h3>'
        f'<div class="markdown-body quick-layer">{md_to_html(quick)}</div>'
        f'<details class="detail-layer"{detail_attr}><summary>詳細版</summary>'
        f'<div class="markdown-body">{md_to_html(body)}</div></details>'
        f'</section>'
    )


def render_quiz_card(body):
    quizzes = parse_quizzes(body)
    if not quizzes:
        return render_card("理解檢查", body, "quiz") if body.strip() else ""
    chunks = ['<section class="study-card quiz-card" id="quiz"><h3>理解檢查</h3>']
    for quiz in quizzes:
        chunks.append(f'<div class="quiz-block" data-answer="{html.escape(quiz["answer"])}">')
        chunks.append(f'<p class="quiz-question">Q{html.escape(quiz["num"])}. {html.escape(quiz["question"])}</p>')
        for key, label in quiz["options"].items():
            chunks.append(f'<button type="button" class="quiz-option" data-option="{key}"><span>{key}</span>{html.escape(label)}</button>')
        chunks.append(f'<p class="quiz-feedback" data-explanation="{html.escape(quiz["explanation"])}"></p>')
        chunks.append("</div>")
    chunks.append("</section>")
    return "".join(chunks)


def render_article(paper, idx):
    ss, ts = paper["summary_sections"], paper["study_sections"]
    date_tag = paper["date"][5:].replace("-", "/")
    tag_html = "".join(f'<span class="paper-tag">{html.escape(tag)}</span>' for tag in paper["tags"])
    data_tags = "|".join(paper["tags"])
    summary_body = strip_meta_sections(ss, [
        "為什麼要研究這個？（研究動機）",
        "他們做了什麼？（研究方法）",
        "驚人發現與具體數據（關鍵結果）",
        "這對我有什麼意義？（實際應用50字內）",
        "這對我有什麼意義？（實際應用）",
    ]) or paper["summary"]
    overview = get_section(ts, "30秒看懂這篇論文", "30 秒看懂這篇論文")
    study_cards = [
        ("30 秒看懂這篇論文", overview, "overview"),
        ("先備知識", get_section(ts, "先備知識"), "prerequisites"),
        ("重要名詞", get_section(ts, "重要名詞"), "terms"),
        ("研究動機", get_section(ts, "研究動機", "脈絡梳理"), "motivation"),
        ("方法流程", get_section(ts, "方法流程"), "method"),
        ("觀念確認", get_section(ts, "觀念確認"), "concepts"),
    ]
    cards = "".join(render_card(name, body, anchor) for name, body, anchor in study_cards if body.strip())
    cards += render_quiz_card(get_section(ts, "理解檢查"))
    if not cards:
        cards = render_card("Study Mode", paper["study"] or "尚未提供 Study Mode 內容。")
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
                <div class="mode-eyebrow">Academic Brief</div>
                <h2>學術早報</h2>
                <div class="markdown-body">{md_to_html(summary_body)}</div>
              </section>
              <section class="study-panel" hidden>
                <div class="study-hero">
                  <div>
                    <p class="hk-tag">[ {html.escape(date_tag)} ]</p>
                    <div class="mode-eyebrow">Study Mode</div>
                    <h2>{html.escape(paper["title"])}</h2>
                    <p>{html.escape(paper["eng_title"])}</p>
                    <div class="study-core"><span>CORE</span>{html.escape(paper["core"])}</div>
                    <div class="paper-tags">{tag_html}</div>
                  </div>
                  <button class="mini-btn" type="button" data-close-study>回到 Summary</button>
                </div>
                <div class="study-layout">
                  <main class="card-grid">{cards}</main>
                  <aside class="study-rail">
                    <h3>學習導覽</h3>
                    <p>本篇學習路徑</p>
                    <a class="active" href="#overview"><span>1</span>Overview<small>總覽</small></a>
                    <a href="#prerequisites"><span>2</span>Prerequisites<small>先備知識</small></a>
                    <a href="#terms"><span>3</span>Key Terms<small>重要名詞</small></a>
                    <a href="#motivation"><span>4</span>Motivation<small>研究動機</small></a>
                    <a href="#method"><span>5</span>Method<small>方法流程</small></a>
                    <a href="#concepts"><span>6</span>Concepts<small>觀念確認</small></a>
                    <a href="#quiz"><span>7</span>Quiz<small>理解檢查</small></a>
                    <div class="study-tip"><strong>學習小提示</strong><br>先看快速版建立地圖，再展開詳細版補足細節。</div>
                  </aside>
                </div>
              </section>
            </div>
          </div>
          <div class="hk-footer"><div class="hk-logo">HUMANKIND <span>+</span> GEOMATICS</div><div class="hk-scroll-hint">SWIPE RIGHT</div></div>
        </div>
      </section>'''


def render_page(papers):
    filters = "".join(f'<button type="button" data-filter="{html.escape(tag)}">{html.escape(tag)}</button>' for tag in ALLOWED_TAGS)
    slides = "".join(render_article(p, i) for i, p in enumerate(papers, 1))
    return f'''<!DOCTYPE html><html lang="zh-TW"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Arxiv Paper Study Library</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css"><link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@700;900&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet"><style>{page_style()}</style></head><body><nav class="filterbar"><strong>Arxiv Paper Library</strong><div class="filters"><button type="button" data-filter="__all" class="active">全部</button>{filters}</div></nav><div class="swiper"><div class="swiper-wrapper">{slides}</div></div><script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script><script>{page_script()}</script></body></html>'''


def page_style():
    return r'''
:root{--hk-bg:#f8f8f8;--hk-black:#0a0a0a;--hk-red:#e5232e;--hk-gray:#dfdfdf;--soft:#f4f4f2;--serif:'Noto Serif TC',serif;--sans:'Noto Sans TC',sans-serif}*{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth}body,html{height:100%;overflow:hidden;background:var(--hk-bg);color:var(--hk-black);font-family:var(--sans)}.filterbar{position:fixed;left:0;right:0;top:0;z-index:10;height:54px;display:flex;align-items:center;justify-content:space-between;gap:18px;padding:0 34px;border-bottom:1px solid var(--hk-gray);background:rgba(248,248,248,.94);backdrop-filter:blur(8px)}.filterbar strong{font-weight:900;letter-spacing:1px}.filters{display:flex;gap:8px;overflow:auto}.filters button,.mini-btn{border:1px solid var(--hk-black);background:#fff;border-radius:5px;padding:7px 10px;font:inherit;font-size:12px;font-weight:800;white-space:nowrap;cursor:pointer}.filters button.active{background:var(--hk-black);color:#fff}.swiper{width:100%;height:100vh;padding-top:54px}.hk-container{width:100%;height:calc(100vh - 54px);padding:42px 52px 30px;display:flex;flex-direction:column;position:relative;z-index:1}.hk-background-text{position:absolute;top:5%;right:5%;font-size:18vw;font-weight:900;color:rgba(0,0,0,.028);z-index:0;pointer-events:none;white-space:nowrap}.hk-grid{display:grid;grid-template-columns:.92fr 1.38fr;gap:42px;z-index:1;flex-grow:1;min-height:0;margin-bottom:20px}.hk-left-col{min-width:0}.hk-right-col{position:relative;overflow-y:auto;padding-right:14px;scrollbar-width:thin;scrollbar-color:var(--hk-black) transparent}.hk-tag{font-weight:800;margin-bottom:8px}.hk-main-title{font-family:var(--serif);font-size:clamp(2rem,4vw,4.8rem);line-height:1.08;font-weight:900;letter-spacing:0;margin-bottom:12px}.hk-eng-subtitle{font-size:.88rem;color:#888;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:22px}.hk-core-statement{display:flex;gap:16px;align-items:flex-start;margin-bottom:18px}.hk-label{background:var(--hk-black);color:#fff;padding:4px 10px;font-size:.7rem;font-weight:900;margin-top:3px}.hk-core-statement p{font-size:1.14rem;font-family:var(--serif);line-height:1.55;font-weight:800}.paper-tags{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0}.paper-tag{background:#fff;border:1px solid var(--hk-gray);border-radius:999px;padding:7px 10px;font-size:12px;font-weight:900;color:#333}.hero-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:20px}.hk-link-btn{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:0 18px;border:2px solid var(--hk-black);border-radius:5px;color:var(--hk-black);text-decoration:none;font-weight:900;background:#fff;cursor:pointer;font:inherit}.hk-link-btn.dark{background:var(--hk-black);color:#fff}.summary-panel,.study-panel{background:rgba(255,255,255,.78);border:1px solid var(--hk-gray);border-radius:7px;padding:20px}.mode-eyebrow{color:var(--hk-red);font-weight:900;text-transform:uppercase;letter-spacing:1px;font-size:12px}.summary-panel h2,.study-head h2{font-size:24px;margin:4px 0 14px}.markdown-body{font-size:15px;line-height:1.78}.markdown-body h3{font-family:var(--serif);font-size:1.2rem;margin:20px 0 10px;border-bottom:2px solid var(--hk-black);display:inline-block}.markdown-body p{margin-bottom:12px;text-align:justify}.markdown-body strong,.markdown-body b{color:var(--hk-red);font-weight:900}.markdown-body ul,.markdown-body ol{padding-left:20px;margin-bottom:10px}.markdown-body li{padding:5px 0;line-height:1.65}.markdown-body table{width:100%;border-collapse:separate;border-spacing:0;margin:8px 0 18px;border:1px solid var(--hk-gray);border-radius:7px;overflow:hidden;background:#fff}.markdown-body th{background:var(--hk-black);color:#fff;text-align:left;padding:10px}.markdown-body td{border-top:1px solid var(--hk-gray);padding:12px;vertical-align:top}.markdown-body td:first-child{width:34%;font-weight:900;color:var(--hk-red)}.study-head{display:flex;justify-content:space-between;gap:12px;align-items:start;margin-bottom:12px}.study-layout{display:grid;grid-template-columns:minmax(0,1fr) 210px;gap:18px;align-items:start}.card-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.study-card{background:#fff;border:1px solid var(--hk-gray);border-radius:7px;padding:15px;min-width:0}.study-card h3{font-size:18px;color:var(--hk-black);margin-bottom:10px}.study-card h3:before{content:'◎';color:var(--hk-red);margin-right:8px}.study-card#terms,.quiz-card{grid-column:1/-1}.study-rail{position:sticky;top:0;background:#fff;border-left:1px solid var(--hk-gray);padding:4px 0 0 18px;min-height:480px}.study-rail h3{font-size:18px;margin-bottom:12px}.study-rail p{font-size:13px;color:#666;padding-bottom:12px;border-bottom:1px solid var(--hk-gray);margin-bottom:14px}.study-rail a{display:grid;grid-template-columns:28px 1fr;gap:10px;text-decoration:none;color:#111;margin:0 0 15px;align-items:start}.study-rail span{width:24px;height:24px;border:1px solid #bbb;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:900;color:#666}.study-rail a:first-of-type span{background:var(--hk-red);border-color:var(--hk-red);color:#fff}.study-rail small{grid-column:2;color:#555;font-size:12px;margin-top:2px}.study-tip{border:1px solid var(--hk-gray);border-radius:7px;padding:14px;margin-top:28px;font-size:13px;line-height:1.7}.study-tip strong{color:var(--hk-red)}.quiz-block{border-top:1px solid var(--hk-gray);padding-top:12px;margin-top:12px}.quiz-block:first-of-type{border-top:0;margin-top:0;padding-top:0}.quiz-question{font-weight:900;margin-bottom:10px}.quiz-option{width:100%;display:flex;gap:10px;align-items:flex-start;text-align:left;background:#fff;border:1px solid var(--hk-gray);border-radius:7px;padding:10px 12px;margin:7px 0;font:inherit;cursor:pointer}.quiz-option span{width:20px;height:20px;border-radius:50%;border:1px solid #ccc;display:inline-flex;align-items:center;justify-content:center;font-size:12px;flex:0 0 auto}.quiz-option.correct{border-color:var(--hk-red);background:#fff1f2}.quiz-option.correct span{background:var(--hk-red);border-color:var(--hk-red);color:#fff}.quiz-option.wrong{border-color:#999;background:#f1f1f1;color:#777}.quiz-feedback{font-size:14px;margin-top:8px;color:#333;background:#f7f7f7;border-radius:7px;padding:10px;display:none}.quiz-feedback.show{display:block}.hk-footer{flex-shrink:0;display:flex;justify-content:space-between;align-items:flex-end;border-top:1px solid #000;padding-top:14px;z-index:2;background:var(--hk-bg)}.hk-logo{font-weight:900;letter-spacing:2px}.hk-logo span{color:var(--hk-red)}.hk-scroll-hint{font-size:.78rem;letter-spacing:3px;font-weight:800}.paper-slide.hidden{display:none!important}@media(max-width:1120px){.hk-grid{grid-template-columns:1fr;gap:24px}.hk-left-col{max-width:880px}.study-layout{grid-template-columns:1fr}.study-rail{position:relative;border-left:0;border-top:1px solid var(--hk-gray);padding:16px 0 0;min-height:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.study-rail h3,.study-rail p,.study-tip{grid-column:1/-1}.study-rail a{margin-bottom:8px}}@media(max-width:760px){body,html{overflow:auto}.filterbar{position:sticky;height:auto;display:block;padding:12px 18px}.filters{margin-top:10px}.swiper{height:auto;padding-top:0}.hk-container{height:auto;min-height:100vh;padding:24px 18px}.hk-main-title{font-size:2.35rem}.card-grid{grid-template-columns:1fr}.hk-footer{display:none}.hk-right-col{overflow:visible;padding-right:0}.study-rail{grid-template-columns:1fr}.hero-actions{display:grid}.hk-link-btn{width:100%}}
.paper-slide.study-active .hk-container{padding:32px 44px 26px}.paper-slide.study-active .hk-background-text{font-size:16vw;right:18%;top:10%;color:rgba(0,0,0,.025)}.paper-slide.study-active .hk-grid{grid-template-columns:260px minmax(0,1fr);gap:28px}.paper-slide.study-active .hk-left-col{border-right:1px solid var(--hk-gray);padding-right:22px;display:flex;flex-direction:column}.paper-slide.study-active .hk-main-title{font-size:1.45rem;line-height:1.28;font-family:var(--sans);font-weight:900;margin:10px 0}.paper-slide.study-active .hk-eng-subtitle{font-size:.68rem;line-height:1.45;margin-bottom:14px}.paper-slide.study-active .hk-core-statement{display:block;margin-top:8px}.paper-slide.study-active .hk-label{display:inline-block;margin:0 0 8px}.paper-slide.study-active .hk-core-statement p{font-size:.98rem;line-height:1.55;font-family:var(--sans);font-weight:600}.paper-slide.study-active .paper-tags{margin-top:auto}.paper-slide.study-active .hero-actions{display:none}.paper-slide.study-active .hk-right-col{overflow-y:auto;padding-right:20px}.paper-slide.study-active .study-panel{display:block;background:rgba(255,255,255,.84);border:1px solid var(--hk-gray);padding:28px;border-radius:7px;min-height:100%}.paper-slide.study-active .study-head{border-bottom:1px solid var(--hk-gray);padding-bottom:18px;margin-bottom:22px}.paper-slide.study-active .study-head h2{font-size:2rem;line-height:1.2}.paper-slide.study-active .study-layout{grid-template-columns:minmax(0,1fr) 250px;gap:32px}.paper-slide.study-active .card-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.paper-slide.study-active .study-card{padding:22px;border-radius:7px;background:#fff}.paper-slide.study-active .study-card h3{font-size:1.35rem;margin-bottom:16px}.paper-slide.study-active .markdown-body{font-size:1.15rem;line-height:1.92}.paper-slide.study-active .markdown-body p{margin-bottom:16px}.paper-slide.study-active .markdown-body li{padding:8px 0;line-height:1.9}.paper-slide.study-active .markdown-body strong,.paper-slide.study-active .markdown-body b{color:var(--hk-red);font-weight:500}.paper-slide.study-active .study-rail{padding-left:28px;min-height:620px}.paper-slide.study-active .study-rail h3{font-size:1.35rem}.paper-slide.study-active .study-rail a{grid-template-columns:34px 1fr;font-size:1.05rem;margin-bottom:20px}.paper-slide.study-active .study-rail span{width:30px;height:30px}.paper-slide.study-active .study-rail small{font-size:.88rem}.paper-slide.study-active .study-tip{font-size:.95rem}.paper-slide.study-active .quiz-question{font-size:1.08rem}.paper-slide.study-active .quiz-option{font-size:1.02rem;padding:13px 14px}.paper-slide.study-active .quiz-feedback{font-size:1rem;line-height:1.7}.paper-slide.study-active .hk-footer{margin-top:18px}
@media(max-width:1120px){.paper-slide.study-active .hk-grid{grid-template-columns:1fr}.paper-slide.study-active .hk-left-col{border-right:0;border-bottom:1px solid var(--hk-gray);padding:0 0 16px}.paper-slide.study-active .hk-main-title{font-size:1.6rem}.paper-slide.study-active .hk-core-statement,.paper-slide.study-active .paper-tags{display:none}.paper-slide.study-active .study-layout{grid-template-columns:1fr}.paper-slide.study-active .study-rail{min-height:0;padding-left:0}}@media(max-width:760px){.paper-slide.study-active .hk-container{padding:18px}.paper-slide.study-active .study-panel{padding:18px}.paper-slide.study-active .card-grid{grid-template-columns:1fr}.paper-slide.study-active .markdown-body{font-size:1.05rem}.paper-slide.study-active .study-head{display:block}.paper-slide.study-active .mini-btn{margin-top:12px}}

.summary-panel{background:transparent;border:0;padding:4px 0 0}.summary-panel h2{font-family:var(--serif);font-size:2.1rem;line-height:1.15;margin:6px 0 22px}.summary-panel .markdown-body{font-size:1.04rem;line-height:1.9}.summary-panel .markdown-body h3{font-family:var(--sans);font-size:1.1rem;border-bottom:0;border-left:3px solid var(--hk-red);padding-left:10px;margin-top:26px}.summary-panel .markdown-body strong,.summary-panel .markdown-body b{color:var(--hk-red);font-weight:500}.summary-panel .markdown-body p{text-align:left}.paper-slide.study-active .hk-container{height:calc(100vh - 54px);overflow:hidden;padding:34px 52px 28px}.paper-slide.study-active .hk-background-text{content:'STUDY';font-size:18vw;right:9%;top:9%;color:rgba(0,0,0,.026)}.paper-slide.study-active .hk-grid{display:block;min-height:0;margin-bottom:16px}.paper-slide.study-active .hk-left-col{display:none}.paper-slide.study-active .hk-right-col{height:100%;overflow-y:auto;padding-right:16px}.paper-slide.study-active .summary-panel{display:none}.paper-slide.study-active .study-panel{display:block;background:transparent;border:0;padding:0;min-height:100%}.paper-slide.study-active .study-hero{display:flex;justify-content:space-between;gap:28px;align-items:flex-start;border-bottom:1px solid var(--hk-gray);padding-bottom:22px;margin-bottom:22px}.paper-slide.study-active .study-hero h2{font-family:var(--serif);font-size:clamp(2.2rem,4.8vw,5.8rem);line-height:1.04;letter-spacing:0;max-width:980px}.paper-slide.study-active .study-hero>div>p:not(.hk-tag){color:#8a8a8a;text-transform:uppercase;letter-spacing:1.5px;line-height:1.45;margin:10px 0 14px;max-width:780px}.study-core{display:flex;gap:12px;align-items:flex-start;max-width:980px;font-size:1.08rem;line-height:1.65}.study-core span{background:#000;color:#fff;font-size:.72rem;font-weight:900;padding:4px 9px;line-height:1}.paper-slide.study-active .study-layout{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:34px;align-items:start}.paper-slide.study-active .card-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.paper-slide.study-active .study-card{background:#fff;border:1px solid var(--hk-gray);border-radius:7px;padding:20px;min-height:190px}.paper-slide.study-active .study-card#overview,.paper-slide.study-active .study-card#terms,.paper-slide.study-active .study-card#method,.paper-slide.study-active .quiz-card{grid-column:span 2}.card-kicker{font-size:.72rem;color:var(--hk-red);text-transform:uppercase;letter-spacing:1px;font-weight:500;margin-bottom:7px}.paper-slide.study-active .study-card h3{font-size:1.28rem;margin-bottom:12px}.paper-slide.study-active .study-card h3:before{content:'◎';color:var(--hk-red);margin-right:8px}.paper-slide.study-active .quick-layer{font-size:1.05rem;line-height:1.85}.detail-layer{border-top:1px solid var(--hk-gray);margin-top:14px;padding-top:10px}.detail-layer summary{cursor:pointer;font-weight:800;font-size:.92rem}.detail-layer .markdown-body{font-size:1rem;line-height:1.86;margin-top:10px}.paper-slide.study-active .markdown-body strong,.paper-slide.study-active .markdown-body b{color:var(--hk-red);font-weight:500}.paper-slide.study-active .study-rail{position:sticky;top:0;background:#fff;border-left:1px solid var(--hk-gray);padding:10px 0 0 26px;min-height:620px}.paper-slide.study-active .study-rail h3{font-size:1.35rem;margin-bottom:16px}.paper-slide.study-active .study-rail p{font-size:.95rem}.paper-slide.study-active .study-rail a{display:grid;grid-template-columns:34px 1fr;gap:12px;font-size:1.05rem;margin:0 0 20px;position:relative}.paper-slide.study-active .study-rail a:before{content:'';position:absolute;left:14px;top:30px;bottom:-18px;width:1px;background:#ddd}.paper-slide.study-active .study-rail a:last-of-type:before{display:none}.paper-slide.study-active .study-rail span{width:30px;height:30px;border-radius:50%;border:1px solid #ccc;background:#fff;color:#666;display:flex;align-items:center;justify-content:center;font-size:.88rem;font-weight:900}.paper-slide.study-active .study-rail a.active{color:var(--hk-red)}.paper-slide.study-active .study-rail a.active span{background:var(--hk-red);border-color:var(--hk-red);color:#fff}.paper-slide.study-active .study-rail small{grid-column:2;color:#555;font-size:.88rem;margin-top:2px}.paper-slide.study-active .quiz-option{font-size:1rem;padding:12px 14px}.paper-slide.study-active .hk-footer{margin-top:14px}@media(max-width:1180px){.paper-slide.study-active .study-layout{grid-template-columns:1fr}.paper-slide.study-active .study-rail{position:relative;min-height:0;border-left:0;border-top:1px solid var(--hk-gray);padding:18px 0 0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.paper-slide.study-active .study-rail h3,.paper-slide.study-active .study-rail p,.paper-slide.study-active .study-tip{grid-column:1/-1}.paper-slide.study-active .study-rail a:before{display:none}}@media(max-width:820px){.paper-slide.study-active .hk-container{height:auto;overflow:visible;padding:22px 18px}.paper-slide.study-active .card-grid{grid-template-columns:1fr}.paper-slide.study-active .study-card#overview,.paper-slide.study-active .study-card#terms,.paper-slide.study-active .study-card#method,.paper-slide.study-active .quiz-card{grid-column:auto}.paper-slide.study-active .study-hero{display:block}.paper-slide.study-active .study-hero h2{font-size:2.4rem}.paper-slide.study-active .mini-btn{margin-top:14px}.paper-slide.study-active .study-rail{grid-template-columns:1fr}.summary-panel .markdown-body{font-size:1rem}}
'''


def page_script():
    return r'''
const swiper=new Swiper('.swiper',{speed:700,mousewheel:{forceToAxis:true},keyboard:{enabled:true},direction:'horizontal'});
document.querySelectorAll('[data-open-study]').forEach(btn=>btn.addEventListener('click',()=>{const slide=btn.closest('.paper-slide');slide.classList.add('study-active');slide.querySelector('.summary-panel').hidden=true;slide.querySelector('.study-panel').hidden=false;}));
document.querySelectorAll('[data-close-study]').forEach(btn=>btn.addEventListener('click',()=>{const slide=btn.closest('.paper-slide');slide.classList.remove('study-active');slide.querySelector('.study-panel').hidden=true;slide.querySelector('.summary-panel').hidden=false;}));
document.querySelectorAll('[data-filter]').forEach(btn=>btn.addEventListener('click',()=>{const tag=btn.dataset.filter;document.querySelectorAll('[data-filter]').forEach(b=>b.classList.toggle('active',b===btn));document.querySelectorAll('.paper-slide').forEach(slide=>{slide.classList.toggle('hidden',tag!=='__all'&&!slide.dataset.tags.split('|').includes(tag));});swiper.update();swiper.slideTo(0,0);}));
document.querySelectorAll('.quiz-block').forEach(block=>{const answer=block.dataset.answer;const feedback=block.querySelector('.quiz-feedback');block.querySelectorAll('.quiz-option').forEach(option=>{option.addEventListener('click',()=>{block.querySelectorAll('.quiz-option').forEach(btn=>{btn.disabled=true;if(btn.dataset.option===answer)btn.classList.add('correct');});if(option.dataset.option!==answer)option.classList.add('wrong');feedback.textContent=(option.dataset.option===answer?'答對了：':'再想一下：')+feedback.dataset.explanation;feedback.classList.add('show');});});});
'''


def update_history(summary_content):
    if not os.path.exists(HISTORY_FILE):
        return
    title = first_line(split_sections(summary_content).get("文獻名稱", ""), "")
    if not title:
        return
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = f.read()
    history = re.sub(rf"(##\s*{re.escape(title)}.*?狀態\s*[:：]\s*)\[PENDING\]", rf"\1[已完成-含StudyMode]", history, flags=re.S)
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
        remotes = subprocess.run(["git", "remote"], capture_output=True, text=True).stdout
        if "origin" not in remotes:
            subprocess.run(["git", "remote", "add", "origin", GITHUB_REMOTE_URL], check=True)
        else:
            subprocess.run(["git", "remote", "set-url", "origin", GITHUB_REMOTE_URL], check=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        commit = subprocess.run(["git", "commit", "-m", f"Auto-Update: {datetime.now().strftime('%m-%d %H:%M')}"], capture_output=True, text=True)
        if commit.returncode != 0:
            print(f"[Git] commit 未建立，可能沒有變更: {commit.stderr.strip() or commit.stdout.strip()}")
        result = subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)
        if result.returncode == 0:
            print("[Git] 已推送到 GitHub Pages。")
        else:
            print(f"[Git Error] push 失敗: {result.stderr.strip()}")
    except Exception as e:
        print(f"[Git Error] 發生例外: {e}")


def mode_merge():
    missing = [p for p in [TEMP_SUMMARY, TEMP_STUDYMODE] if not os.path.exists(p) or os.path.getsize(p) == 0]
    if missing:
        print("[Merge] Summary + Study Mode 尚未全部完成，不會刪除暫存檔。")
        for p in missing:
            print(f"- 缺少或空檔案: {p}")
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
        print("[Render] 沒有可渲染的論文。")
        return
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(render_page(papers))
    print(f"[Render] {OUTPUT_HTML} 已更新，共 {len(papers)} 篇。")
    git_push_auto()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["merge", "render"], required=True)
    args = parser.parse_args()
    if args.mode == "merge":
        mode_merge()
    else:
        mode_render()
