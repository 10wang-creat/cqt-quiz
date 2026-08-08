# cqt-quiz — CQT 品質管制技術師 統計品管備考

線上版（GitHub Pages）：
- 速查筆記（單元入口）：https://10wang-creat.github.io/cqt-quiz/notes.html
  - 甲單元（早上）：…/notes_a.html｜乙單元（下午）：…/notes_b.html
- 題庫練習：https://10wang-creat.github.io/cqt-quiz/index.html

**這個 repo 是唯一的工作來源（single source of truth）。** 所有更新都在這裡進行，OneDrive 的 `CQT品質管理技術師` 資料夾已停用、不再更新。

## 檔案結構

| 檔案 | 角色 |
|---|---|
| `index.html` | 手機離線測驗網頁（題庫練習），內嵌全部題目；作答紀錄存在手機瀏覽器 localStorage。部署到 Pages |
| `notes.html` | 筆記入口頁（選甲/乙單元） |
| `notes_a.html` / `notes_b.html` | 甲/乙單元筆記交付版（各自可印成紙本帶進考場），由對應 md 母版轉出；圖檔 base64 內嵌 |
| `統計品管_甲單元筆記.md` | **甲單元母版**（一～二十九章：基本統計＋管制圖）——改甲的筆記改這份 |
| `統計品管_乙單元筆記.md` | **乙單元母版**（乙一～乙十章：抽樣計畫；檢驗與測試、品質概念待補）——改乙的筆記改這份 |
| `scripts/notes_to_html.py` | md 母版 → `notes.html` 的轉檔腳本 |
| `scripts/quiz_tool.py` | 題庫合併/檢視工具（summary / inject / extract），作用於 `index.html` |
| `圖解/*.png` | 筆記引用的圖解 |

## 更新流程

改筆記（改對應單元的 md 母版）後，重生 HTML：

```bash
python3 scripts/notes_to_html.py 統計品管_甲單元筆記.md notes_a.html index.html
python3 scripts/notes_to_html.py 統計品管_乙單元筆記.md notes_b.html index.html
```

加題庫（新題目 JSON）：

```bash
python3 scripts/quiz_tool.py summary index.html            # 看現況
python3 scripts/quiz_tool.py inject index.html new.json     # 合併（自動編 id、驗證、備份）
```

> ⚠️ 絕不可更動既有題目的 id——手機的作答紀錄以 id 為鍵。

## 部署

改完 commit + push（用 GitHub Desktop 或 git）：

```bash
git add -A && git commit -m "更新筆記/題庫" && git push
```

GitHub Pages 約 1~2 分鐘後生效。

## 注意

- 課程講義 PDF（有著作權）**不放進這個公開 repo**，留在本機／OneDrive 私存。
- 若 GitHub Desktop 出現 `A lock file already exists`（`.git/index.lock`）：關掉 GitHub Desktop、刪掉 `.git/index.lock` 再重開即可。
- 
