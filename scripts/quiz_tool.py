#!/usr/bin/env python3
"""統計題庫練習.html 的題目資料工具。

用法:
  python3 quiz_tool.py extract <app.html> [out.json]   # 取出 DATA 陣列
  python3 quiz_tool.py inject  <app.html> <new.json>   # 合併新題（自動編id、驗證、備份）
  python3 quiz_tool.py summary <app.html>              # 各題庫/章節題數統計

inject 的 new.json 是題目物件陣列，id 欄位可省略（會自動接續編號）。
既有題目的 id 永不變動：使用者手機 localStorage 以 id 記錄作答紀錄。
"""
import sys, json, re, shutil, datetime, collections

MARK = 'const DATA = '

def read_data(path):
    html = open(path, encoding='utf-8').read()
    i = html.index(MARK) + len(MARK)
    j = html.index(';\n', i)
    return html, i, j, json.loads(html[i:j])

def validate(qs, start_id=1):
    errs = []
    seen = set()
    for q in qs:
        qid = q.get('id', '?')
        if qid in seen: errs.append(f"id {qid} 重複")
        seen.add(qid)
        t = q.get('type')
        if t not in ('single', 'multi', 'open'):
            errs.append(f"id {qid}: type 不合法 ({t})"); continue
        if not q.get('q', '').strip(): errs.append(f"id {qid}: 題幹為空")
        if t in ('single', 'multi'):
            ans, opts = q.get('ans') or '', q.get('opts') or {}
            if not ans: errs.append(f"id {qid}: MCQ 缺 ans")
            elif any(a not in opts for a in ans): errs.append(f"id {qid}: ans '{ans}' 有選項不存在於 opts {sorted(opts)}")
            if len(opts) < 2: errs.append(f"id {qid}: 選項少於2個")
            if t == 'single' and len(ans) > 1: errs.append(f"id {qid}: single 但 ans 多字母，應改 multi")
        else:
            if not (q.get('ansText') or q.get('expl')): errs.append(f"id {qid}: open 題缺 ansText/expl")
    return errs

def summary(qs):
    c = collections.Counter((q['src'], q['ch']) for q in qs)
    src_c = collections.Counter(q['src'] for q in qs)
    print(f"總題數 {len(qs)}，flag {sum(1 for q in qs if q.get('flag'))} 題")
    for src, n in src_c.items():
        print(f"  {src}: {n}")
    return c

def main():
    cmd = sys.argv[1]
    html_path = sys.argv[2]
    html, i, j, data = read_data(html_path)
    if cmd == 'extract':
        out = sys.argv[3] if len(sys.argv) > 3 else None
        s = json.dumps(data, ensure_ascii=False, indent=1)
        if out: open(out, 'w', encoding='utf-8').write(s); print(f"{len(data)} 題 → {out}")
        else: print(s)
    elif cmd == 'summary':
        summary(data)
    elif cmd == 'inject':
        new = json.load(open(sys.argv[3], encoding='utf-8'))
        nid = max(q['id'] for q in data) + 1
        for q in new:
            q['id'] = nid; nid += 1
            q.setdefault('opts', {}); q.setdefault('ans', None)
            q.setdefault('ansText', None); q.setdefault('expl', '')
            q.setdefault('flag', False); q.setdefault('num', 0)
        errs = validate(data + new)
        if errs:
            print("❌ 驗證失敗，未寫入："); [print("  " + e) for e in errs]; sys.exit(1)
        bak = html_path + '.bak-' + datetime.date.today().isoformat()
        shutil.copy(html_path, bak)
        merged = data + new
        out_html = html[:i] + json.dumps(merged, ensure_ascii=False) + html[j:]
        open(html_path, 'w', encoding='utf-8').write(out_html)
        # 重讀驗證
        _, _, _, check = read_data(html_path)
        assert len(check) == len(merged)
        print(f"✅ 新增 {len(new)} 題（id {merged[len(data)]['id']}~{nid-1}），總計 {len(merged)} 題。備份：{bak}")
        summary(merged)
    else:
        print(__doc__); sys.exit(1)

if __name__ == '__main__':
    main()
