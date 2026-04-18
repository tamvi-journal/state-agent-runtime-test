# GitHub Push Guide

## 1. Copy the new docs into your repo

Put these files into your local repository under:

```text
docs/
```

Files:
- `project-state-map.md`
- `architecture-overview.md`
- `release-roadmap.md`
- `component-maturity.md`
- `next-build-order.md`
- `github-push-guide.md`

---

## 2. Open PowerShell in the repo root

Example:

```powershell
cd D:\state-memory-agent
```

Check you are in the right folder:

```powershell
git status
```

---

## 3. Verify the docs exist

```powershell
Get-ChildItem .\docs
```

You should see the new markdown files listed.

---

## 4. Stage the files

To stage everything:

```powershell
git add .
```

If you only want to stage the docs:

```powershell
git add docs/project-state-map.md docs/architecture-overview.md docs/release-roadmap.md docs/component-maturity.md docs/next-build-order.md docs/github-push-guide.md
```

---

## 5. Commit

Recommended commit message:

```powershell
git commit -m "R1: add packaging docs, architecture map, and release roadmap"
```

If Git says nothing changed, run:

```powershell
git status
```

and check whether the files are actually in the repo folder.

---

## 6. Push to GitHub

If your current branch is already connected:

```powershell
git push
```

If you need to push current branch explicitly:

```powershell
git branch --show-current
git push origin <your-branch-name>
```

Example:

```powershell
git push origin main
```

---

## 7. Refresh GitHub and verify

On GitHub, verify:
- the new files are in `docs/`
- the latest commit message appears
- file rendering looks clean

---

## 8. If push fails

### Case A — remote rejected
Try:

```powershell
git pull --rebase
git push
```

### Case B — not on the correct branch
Check:

```powershell
git branch
```

Then push the correct branch.

### Case C — GitHub auth popup / token request
Just complete sign-in in the browser or Git Credential Manager prompt, then retry:

```powershell
git push
```

---

## 9. Recommended follow-up

After push, create one small housekeeping commit later if needed:
- fix headings
- add repo root `README` links to these docs
- add milestone labels inside roadmap

But push this package first so the project state is captured.
