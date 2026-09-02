# md 母版 → 送影印店裝訂的 A4 雙面「書本版」PDF（WeasyPrint，純 Python，不需瀏覽器）
# 特色：封面、目錄自動頁碼、每章從新頁開始、奇偶頁鏡像裝訂邊（內側 20mm）、頁尾頁碼＋章名
# 用法: python3 scripts/notes_to_book_pdf.py 統計品管_甲單元筆記.md 甲單元筆記_列印版.pdf 甲單元
import sys, re, base64, os, datetime
import markdown
from weasyprint import HTML

src, out, book = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(src, encoding="utf-8").read()
today = datetime.date.today().isoformat()

# 列印環境沒有彩色 emoji 字型，換成黑白可印的符號（★ ✔ ✘ ⚠ 在 DejaVu Sans 內）
EMOJI = {"⭐": "★", "✅": "✔", "❌": "✘", "⚠️": "⚠", "📌": "■", "🏷️": "▸", "🏷": "▸",
         "🖩": "[計算機]", "🔗": "→", "📋": "▪", "🎯": "◎", "️": ""}
for k, v in EMOJI.items():
    text = text.replace(k, v)

def embed(m):
    p = m.group(1)
    if os.path.exists(p):
        b = base64.b64encode(open(p, "rb").read()).decode()
        return f'<img src="data:image/png;base64,{b}"'
    print("缺少圖檔:", p)
    return m.group(0)

body = markdown.markdown(text, extensions=["tables", "sane_lists"])
body = re.sub(r'<img src="(圖解/[^"]+)"', embed, body)
body = re.sub(r'<h1>.*?</h1>\s*<hr\s*/?>', "", body, count=1, flags=re.S)  # 母版標題改由封面呈現

chapters = []
def h2id(m):
    i = len(chapters)
    title = re.sub(r"<[^>]+>", "", m.group(1))
    chapters.append(title)
    # string-set 讓頁尾能顯示目前章名（去掉 ⭐ 等符號、截短）
    short = re.sub(r"[★■▸✔⚠]+.*$", "", title).strip()[:22]
    return f'<h2 id="ch{i}" data-short="{short}">{m.group(1)}</h2>'
body = re.sub(r"<h2>(.*?)</h2>", h2id, body)

CSS = f"""
@page {{
  size: A4;
  margin: 14mm 14mm 16mm 14mm;
  @bottom-center {{ content: "{book} ─ 第 " counter(page) " 頁"; font-size: 8pt; color: #555; font-family: "Noto Sans CJK TC"; }}
}}
@page :left  {{ margin-left: 14mm; margin-right: 22mm;
  @top-left {{ content: string(chap); font-size: 7.5pt; color: #777; font-family: "Noto Sans CJK TC"; }} }}
@page :right {{ margin-left: 22mm; margin-right: 14mm;
  @top-right {{ content: string(chap); font-size: 7.5pt; color: #777; font-family: "Noto Sans CJK TC"; }} }}
@page cover {{ margin: 0; @bottom-center {{ content: none; }} }}
@page toc {{ @top-left {{ content: none; }} @top-right {{ content: none; }} }}

body {{ font-family: "Noto Sans CJK TC", "DejaVu Sans", sans-serif; font-size: 9.5pt; line-height: 1.45; color: #111; }}
.cover {{ page: cover; height: 297mm; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; background: #1a3a5c; color: #fff; break-after: page; }}
.cover .t1 {{ font-size: 30pt; font-weight: 700; letter-spacing: 2px; }}
.cover .t2 {{ font-size: 16pt; margin-top: 12mm; }}
.cover .t3 {{ font-size: 10pt; margin-top: 30mm; color: #cfd8e3; }}
.tocpage {{ page: toc; break-after: page; }}
.tocpage h1 {{ font-size: 16pt; border-bottom: 2px solid #1a3a5c; padding-bottom: 4px; }}
.toc {{ column-count: 2; column-gap: 8mm; font-size: 9pt; }}
.toc a {{ display: block; color: #111; text-decoration: none; margin: 2px 0; }}
.toc a::after {{ content: leader(". ") target-counter(attr(href), page); }}

h2 {{ break-before: page; string-set: chap attr(data-short); font-size: 13pt; background: #1a3a5c; color: #fff; padding: 4px 8px; border-radius: 3px; margin: 0 0 6px; }}
h3 {{ font-size: 11pt; border-left: 4px solid #1a3a5c; padding-left: 6px; margin: 10px 0 4px; break-after: avoid; }}
h4 {{ font-size: 10pt; margin: 8px 0 3px; break-after: avoid; }}
table {{ border-collapse: collapse; width: 100%; margin: 4px 0; }}
th, td {{ border: 0.6pt solid #999; padding: 2px 5px; font-size: 9pt; vertical-align: top; }}
th {{ background: #e8eef5; }}
tr {{ break-inside: avoid; }}
thead {{ display: table-header-group; }}
blockquote {{ background: #f7eded; border-left: 4px solid #8b1e1e; margin: 5px 0; padding: 3px 8px; break-inside: avoid; }}
blockquote p {{ margin: 2px 0; }}
img {{ max-width: 150mm; height: auto; }}
p {{ margin: 3px 0; }}
code {{ font-family: "Noto Sans Mono CJK TC", monospace; font-size: 8.5pt; background: #f0f0f0; }}
pre {{ background: #f0f0f0; padding: 4px 6px; font-size: 8.5pt; white-space: pre-wrap; }}
ul, ol {{ margin: 3px 0; padding-left: 18px; }}
li {{ margin: 1px 0; }}
hr {{ border: none; border-top: 0.5pt solid #bbb; margin: 6px 0; }}
"""

toc = "".join(f'<a href="#ch{i}">{t}</a>' for i, t in enumerate(chapters))
html = (f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
        f'<div class="cover"><div class="t1">統計品管 考試速查筆記</div>'
        f'<div class="t2">{book}</div>'
        f'<div class="t3">CQT 品質管理技術師　列印版 {today}</div></div>'
        f'<div class="tocpage"><h1>目錄</h1><div class="toc">{toc}</div></div>'
        f'{body}</body></html>')

doc = HTML(string=html, base_url=os.getcwd()).render()
doc.write_pdf(out)
print(f"{out}: {len(chapters)} 章, 共 {len(doc.pages)} 頁")
