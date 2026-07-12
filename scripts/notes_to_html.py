#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統計品管速查筆記 md → 手機友善單一 HTML
用法: python3 notes_to_html.py 統計品管_考試速查筆記.md 輸出.html [題庫連結]
特色: 目錄抽屜、章節折疊、關鍵字搜尋、深色模式、圖解 base64 內嵌、表格橫向捲動
配色: 詣姈夏季冷柔色盤（薰衣草/紫藤/霧藍/鼠尾草/珍珠白/藏藍）
"""
import sys, os, re, base64, datetime
import markdown

def main():
    if len(sys.argv) not in (3, 4):
        print("用法: python3 notes_to_html.py 輸入.md 輸出.html [題庫連結]"); sys.exit(1)
    md_path, out_path = sys.argv[1], sys.argv[2]
    quiz_href = sys.argv[3] if len(sys.argv) == 4 else "index.html"
    base_dir = os.path.dirname(os.path.abspath(md_path))
    text = open(md_path, encoding="utf-8").read()

    body = markdown.markdown(text, extensions=["tables"])

    # 內嵌圖片 base64
    img_count, missing = 0, []
    def embed(m):
        nonlocal img_count
        src = m.group(1)
        p = os.path.join(base_dir, src)
        if not os.path.exists(p):
            missing.append(src); return m.group(0)
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        img_count += 1
        return 'src="data:image/png;base64,%s"' % b64
    body = re.sub(r'src="([^"]+\.png)"', embed, body)

    # 表格包捲動容器
    body = body.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")

    # 依 h2 切章節，包 <section>
    parts = re.split(r"(?=<h2>)", body)
    head_html, secs, toc = parts[0], [], []
    for i, p in enumerate(parts[1:], 1):
        m = re.match(r"<h2>(.*?)</h2>", p, re.S)
        title = re.sub(r"<.*?>", "", m.group(1)) if m else "第%d節" % i
        rest = p[m.end():] if m else p
        toc.append('<a href="#s%d" onclick="closeToc()">%s</a>' % (i, title))
        secs.append(
            '<section id="s%d"><h2 onclick="tg(this)">%s<span class="ar">▾</span></h2>'
            '<div class="sb">%s<button class="fold" onclick="foldSec(this)">▴ 收合本節</button></div></section>' % (i, m.group(1) if m else title, rest))
    today = datetime.date.today().isoformat()

    html = TEMPLATE.replace("{{HEAD}}", head_html).replace("{{SECS}}", "\n".join(secs)) \
        .replace("{{TOC}}", "\n".join(toc)).replace("{{DATE}}", today).replace("{{QUIZ}}", quiz_href)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("章節數(h2): %d" % len(secs))
    print("內嵌圖片: %d" % img_count)
    if missing: print("⚠️ 缺少圖檔: %s" % ", ".join(missing))
    print("輸出: %s (%.0f KB)" % (out_path, os.path.getsize(out_path)/1024))

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>統計品管 考試速查筆記</title>
<style>
:root{--bg:#F0EEF3;--fg:#34435E;--card:#fff;--line:#DFDAE8;--acc:#8981C2;--mark:#D7CBF2;
--th:#ECE8F6;--warn-bg:#FBF0F4;--warn-bd:#E1A2BA;--dim:#7A7F96;}
html.dark{--bg:#1B2231;--fg:#E4E2EC;--card:#242D40;--line:#3B465E;--acc:#BBADD8;--mark:#6D5E9E;
--th:#2D3750;--warn-bg:#39303F;--warn-bd:#C88EA8;--dim:#98A0B6;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 -apple-system,"PingFang TC","Microsoft JhengHei",sans-serif;-webkit-text-size-adjust:100%}
#bar{position:sticky;top:0;z-index:10;display:flex;gap:8px;align-items:center;padding:8px 10px;
background:var(--card);border-bottom:1px solid var(--line)}
#bar button{border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:8px;
padding:6px 10px;font-size:15px}
#q{flex:1;min-width:0;border:1px solid var(--line);background:var(--bg);color:var(--fg);
border-radius:8px;padding:6px 10px;font-size:15px}
#hits{font-size:12px;color:var(--dim);white-space:nowrap}
main{max-width:860px;margin:0 auto;padding:10px 14px 80px}
h1{font-size:22px;margin:14px 0 4px}
.meta{color:var(--dim);font-size:13px;margin-bottom:10px}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;margin:12px 0;overflow:hidden;scroll-margin-top:54px}
.fold{display:block;margin:16px auto 2px;padding:8px 22px;border:1px solid var(--line);background:var(--bg);color:var(--acc);border-radius:20px;font-size:14.5px;cursor:pointer}
h2{font-size:18px;margin:0;padding:12px 14px;cursor:pointer;display:flex;justify-content:space-between;
align-items:center;gap:8px;color:var(--acc)}
h2 .ar{transition:.2s;color:var(--dim)}
section.cl .sb{display:none}
section.cl .ar{transform:rotate(-90deg)}
.sb{padding:0 14px 14px}
h3{font-size:16.5px;margin:18px 0 8px;border-left:4px solid var(--acc);padding-left:8px}
.tw{overflow-x:auto;margin:10px 0;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;font-size:14.5px;min-width:100%}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}
th{background:var(--th);white-space:nowrap}
blockquote{margin:10px 0;padding:8px 12px;background:var(--warn-bg);border-left:4px solid var(--warn-bd);
border-radius:0 8px 8px 0;font-size:15px}
blockquote p{margin:4px 0}
img{max-width:100%;height:auto;border-radius:8px;background:#fff}
code,pre{background:var(--th);border-radius:6px;font-size:14px}
pre{padding:8px;overflow-x:auto}
mark{background:var(--mark);color:inherit;border-radius:2px}
#toc{position:fixed;inset:0 25% 0 0;max-width:320px;background:var(--card);z-index:20;
transform:translateX(-105%);transition:.25s;overflow-y:auto;padding:14px;border-right:1px solid var(--line)}
#toc.open{transform:none;box-shadow:4px 0 20px rgba(0,0,0,.3)}
#toc a{display:block;padding:9px 6px;color:var(--fg);text-decoration:none;border-bottom:1px solid var(--line);font-size:15px}
#ov{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:15;display:none}
#ov.on{display:block}
#top{position:fixed;right:14px;bottom:18px;z-index:10;border:1px solid var(--line);background:var(--card);
color:var(--fg);border-radius:50%;width:42px;height:42px;font-size:18px;display:none}
.tocbtns{display:flex;gap:8px;margin-bottom:8px}
.tocbtns button{flex:1;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:8px;padding:6px}
</style>
</head>
<body>
<div id="bar">
<button onclick="openToc()">☰</button>
<input id="q" type="search" placeholder="搜尋關鍵字…" oninput="doSearch()">
<span id="hits"></span>
<button onclick="location.href='{{QUIZ}}'" title="題庫練習">✏️</button>
<button onclick="toggleDark()">🌓</button>
</div>
<nav id="toc"><div class="tocbtns"><button onclick="setAll(false)">全部展開</button><button onclick="setAll(true)">全部收合</button></div>{{TOC}}<a href="{{QUIZ}}" style="color:var(--acc);font-weight:700">✏️ 前往題庫練習</a></nav>
<div id="ov" onclick="closeToc()"></div>
<main>
{{HEAD}}
<p class="meta">更新：{{DATE}}｜點章節標題可折疊｜考前印紙本請用 PDF 版</p>
{{SECS}}
</main>
<button id="top" onclick="scrollTo({top:0,behavior:'smooth'})">↑</button>
<script>
if(localStorage.getItem('nk-dark')==='1'||(localStorage.getItem('nk-dark')===null&&matchMedia('(prefers-color-scheme: dark)').matches))document.documentElement.classList.add('dark');
function toggleDark(){var d=document.documentElement.classList.toggle('dark');localStorage.setItem('nk-dark',d?'1':'0');}
function tg(h){h.parentNode.classList.toggle('cl');}
function foldSec(b){var s=b.closest('section');s.classList.add('cl');s.scrollIntoView({block:'start'});}
function setAll(cl){document.querySelectorAll('section').forEach(function(s){s.classList.toggle('cl',cl);});closeToc();}
function openToc(){document.getElementById('toc').classList.add('open');document.getElementById('ov').classList.add('on');}
function closeToc(){document.getElementById('toc').classList.remove('open');document.getElementById('ov').classList.remove('on');}
addEventListener('scroll',function(){document.getElementById('top').style.display=scrollY>600?'block':'none';});
var tmr;
function doSearch(){clearTimeout(tmr);tmr=setTimeout(run,200);}
function clearMarks(){document.querySelectorAll('mark.sh').forEach(function(m){m.replaceWith(m.textContent);});
document.querySelectorAll('main mark').length||document.normalize();}
function run(){
 var q=document.getElementById('q').value.trim().toLowerCase();
 document.querySelectorAll('mark.sh').forEach(function(m){var t=document.createTextNode(m.textContent);m.parentNode.replaceChild(t,m);});
 var hits=0;
 document.querySelectorAll('section').forEach(function(sec){
  if(!q){sec.style.display='';sec.classList.remove('cl');return;}
  var found=false,walker=document.createTreeWalker(sec,NodeFilter.SHOW_TEXT),nodes=[];
  while(walker.nextNode())nodes.push(walker.currentNode);
  nodes.forEach(function(n){
   var t=n.nodeValue,i=t.toLowerCase().indexOf(q);
   if(i<0)return;
   found=true;
   var frag=document.createDocumentFragment(),pos=0,low=t.toLowerCase();
   while(i>=0){frag.appendChild(document.createTextNode(t.slice(pos,i)));
    var mk=document.createElement('mark');mk.className='sh';mk.textContent=t.slice(i,i+q.length);frag.appendChild(mk);
    hits++;pos=i+q.length;i=low.indexOf(q,pos);}
   frag.appendChild(document.createTextNode(t.slice(pos)));
   n.parentNode.replaceChild(frag,n);});
  sec.style.display=found?'':'none';
  if(found)sec.classList.remove('cl');});
 document.getElementById('hits').textContent=q?hits+' 處':'';
}
</script>
</body>
</html>"""

if __name__ == "__main__":
    main()
