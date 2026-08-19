# md 母版 → 列印版 A4 PDF（Playwright + Chromium，兩段式產生目錄頁碼）
# 用法: python3 notes_to_print_pdf.py 母版.md 輸出.pdf 冊名
import sys, re, base64, os, json
import markdown
from playwright.sync_api import sync_playwright

src, out, book = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(src, encoding="utf-8").read()

def embed(m):
    p = m.group(1)
    if os.path.exists(p):
        b = base64.b64encode(open(p, "rb").read()).decode()
        return f'<img src="data:image/png;base64,{b}"'
    return m.group(0)

body = markdown.markdown(text, extensions=["tables", "sane_lists"])
body = re.sub(r'<img src="(圖解/[^"]+)"', embed, body)

chapters = []
def h2id(m):
    i = len(chapters)
    chapters.append(re.sub(r"<[^>]+>", "", m.group(1)))
    return f'<h2 id="ch{i}">{m.group(1)}</h2>'
body = re.sub(r"<h2>(.*?)</h2>", h2id, body)

CSS = """
body { font-family: "Noto Sans CJK TC", sans-serif; font-size: 9.5pt; line-height: 1.45; color:#111; margin:0; }
h1 { font-size: 16pt; margin: 0 0 6px; }
h2 { break-before: page; font-size: 13pt; background:#1a3a5c; color:#fff; padding:4px 8px; border-radius:3px; margin: 0 0 6px; -webkit-print-color-adjust: exact; }
h3 { font-size: 11pt; border-left: 4px solid #1a3a5c; padding-left: 6px; margin: 10px 0 4px; }
table { border-collapse: collapse; width: 100%; margin: 4px 0; }
th, td { border: 0.6pt solid #999; padding: 2px 5px; font-size: 9pt; }
th { background: #e8eef5; -webkit-print-color-adjust: exact; }
tr { break-inside: avoid; }
blockquote { background: #fdf3f3; border-left: 4px solid #c0392b; margin: 5px 0; padding: 3px 8px; break-inside: avoid; -webkit-print-color-adjust: exact; }
img { max-width: 150mm; height: auto; }
code { font-family: "Noto Sans Mono CJK TC", monospace; font-size: 8.5pt; background:#f0f0f0; }
ul, ol { margin: 3px 0; padding-left: 18px; }
li { margin: 1px 0; }
hr { border: none; border-top: 0.5pt solid #bbb; }
.toc { column-count: 2; column-gap: 8mm; font-size: 9pt; }
.tocline { margin: 1.5px 0; display: flex; }
.toc .t { flex: 1; }
.toc .p { color:#555; padding-left: 4px; }
"""

def make_doc(pagenums):
    toc = "".join(
        f'<div class="tocline"><span class="t">{t}</span><span class="p">{pagenums.get(i,"–")}</span></div>'
        for i, t in enumerate(chapters))
    return (f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'<h1>{book}・統計品管速查筆記（列印版 2026-08-16）</h1>'
            f'<div class="toc">{toc}</div>{body}</body></html>')

FOOTER = ('<div style="font-size:8px; width:100%; text-align:center; color:#666;">'
          f'{book} ─ 第 <span class="pageNumber"></span> / <span class="totalPages"></span> 頁</div>')
PDFOPT = dict(format="A4",
              margin={"top": "13mm", "bottom": "15mm", "left": "12mm", "right": "12mm"},
              display_header_footer=True, header_template="<span></span>",
              footer_template=FOOTER, print_background=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium/chrome-linux/chrome"
                                if os.path.exists("/opt/pw-browsers/chromium/chrome-linux/chrome") else None)
    page = browser.new_page()

    # 第一遍：無頁碼目錄，量出每章起始頁
    page.set_content(make_doc({}), wait_until="load")
    page.pdf(path="/tmp/_pass1.pdf", **PDFOPT)
    import pypdf
    import unicodedata
    norm = lambda s: re.sub(r"[^一-鿿A-Za-z0-9]", "", unicodedata.normalize("NFKC", s))
    r = pypdf.PdfReader("/tmp/_pass1.pdf")
    texts = [norm(pg.extract_text() or "") for pg in r.pages]
    pagenums, cursor = {}, 1  # 從第 2 頁開始找（跳過封面/目錄）
    for i, c in enumerate(chapters):
        key = norm(c)[:10] or norm(c)
        for pno in range(cursor, len(texts)):
            if key in texts[pno]:
                pagenums[i] = pno + 1
                cursor = pno  # 章節頁碼遞增（同頁可有多章開頭時不前進）
                break

    # 第二遍：帶真實頁碼（目錄行數不變，分頁不會位移）
    page.set_content(make_doc(pagenums), wait_until="load")
    page.pdf(path=out, **PDFOPT)
    browser.close()

n = len(pypdf.PdfReader(out).pages)
print(f"{out}: {len(chapters)} 章（目錄抓到頁碼 {len(pagenums)} 章）, 共 {n} 頁")
