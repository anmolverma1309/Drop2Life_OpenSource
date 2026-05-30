# Automation: GitHub Activity Generator Runner

This folder provides a small wrapper around the cloned `github-activity-generator` repo so you can run it with one command and keep your parameters in one place.

## Prerequisites
- Python 3.8+
- A GitHub repository that is empty (no README, no license, no .gitignore)
- The `github-activity-generator` repo is cloned next to this folder

## Quick Start
1) Create an empty GitHub repo and copy the URL.
2) (Optional) Edit `automation/config.json` to set defaults.
3) Open PowerShell in the workspace root.
4) Run:

```powershell
./automation/run.ps1 -RepoUrl "https://github.com/YOUR_USERNAME/YOUR_REPO.git"
```

Or double-click `automation/run.cmd` after you set `RepoUrl` in `config.json`.

## Ready Checklist
- `RepoUrl` in `automation/config.json` points to an empty repo
- Python 3.8+ is on PATH
- `github-activity-generator` is cloned next to this folder

## Options
```powershell
./automation/run.ps1 \
  -RepoUrl "https://github.com/YOUR_USERNAME/YOUR_REPO.git" \
  -DaysBefore 365 \
  -DaysAfter 0 \
  -MaxCommits 10 \
  -Frequency 80 \
  -NoWeekends
```

## Config File
You can set defaults in `automation/config.json`. Any command-line options you pass will override the config values.

If Python is not on PATH, set `PythonPath` to the full path of your `python.exe`.

## Notes
- This generates artificial commit history.
- Use responsibly and only where appropriate.
