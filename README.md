# cqt-quiz — CQT 品質管制技術師 統計品管備考

線上版（GitHub Pages）：
- 速查筆記：https://10wang-creat.github.io/cqt-quiz/notes.html
- 題庫練習：https://10wang-creat.github.io/cqt-quiz/index.html

**這個 repo 是唯一的工作來源（single source of truth）。** 所有更新都在這裡進行，OneDrive 的 `CQT品質管理技術師` 資料夾已停用、不再更新。

## 檔案結構

| 檔案 | 角色 |
|---|---|
| `index.html` | 手機離線測驗網頁（題庫練習），內嵌全部題目；作答紀錄存在手機瀏覽器 localStorage。部署到 Pages |
| `notes.html` | 速查筆記交付版，由 md 母版轉出；圖檔以 base64 內嵌。部署到 Pages |
| `統計品管_考試速查筆記.md` | 筆記**母版**（Markdown），所有筆記修改都改這份 |
| `scripts/notes_to_html.py` | md 母版 → `notes.html` 的轉檔腳本 |
| `scripts/quiz_tool.py` | 題庫合併/檢視工具（summary / inject / extract），作用於 `index.html` |
| `圖解/*.png` | 筆記引用的圖解 |

## 更新流程

改筆記（改 `統計品管_考試速查筆記.md`）後，重生 HTML：

```bash
python3 scripts/notes_to_html.py 統計品管_考試速查筆記.md notes.html index.html
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
