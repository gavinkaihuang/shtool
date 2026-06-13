# OpenCode Agent Onboarding Instructions (`AGENTS.md`)

This repository is a collection of standalone personal script utilities (Python and Bash) under `/Users/huangkai/sourcecodes/shtool/` (known as "shtool").

---

## 🛠️ Environment & Python Setup

- **Virtual Environment**: A local virtualenv exists at `.venv/` at the root directory.
- **Python Path**: Always run Python scripts using the virtualenv interpreter: `/Users/huangkai/sourcecodes/shtool/.venv/bin/python` (or ensure `.venv/bin/activate` is sourced).
- **Core Dependencies**: `requests`, `beautifulsoup4`, `google-generativeai`, `pandas`, `fitz` (PyMuPDF).

---

## ⚠️ High-Risk Gotchas

- **Sensitive Configurations**: 
  - `anki/config.py` contains active Gemini API credentials.
  - `config.ini` contains Telegram bot configurations.
  - **Rule**: Never overwrite these configuration files with placeholder templates (`config.ini.sample`). Always `read` them first before any modifying edits.
- **Git State**: `.gitignore` contains git conflict markers from prior manual stashes. Do not clean up or touch `.gitignore` unless explicitly instructed.

---

## 🔄 Core Scripts & Workflows

### 1. Disk Cleanup & File Deletion (`run_cleaners.py`)
- **Wrapper Flow**: Sequentially runs `delete_small_videos.py` (deletes `<100MB` videos), `find_and_delete_files.py` (removes `.txt`, `.url`, `.html`, `.apk`), and `delete_empty_folder.py`.
- **Command**:
  ```bash
  python run_cleaners.py /path/to/target --no-confirm
  ```
  *(Omit `--no-confirm` to prompt for interactive deletion confirmation).*

### 2. Multi-Stage Deduplication (`scan&delete/`)
- **Required Order**:
  1. Run `python scan_dupes.py` to identify duplicates and write state to `duplicate_names.json`.
  2. Run `python clean_dupes.py` to inspect / preview.
  3. Run `python clean_dupes.py --execute` to perform actual file deletions.

### 3. Novel Spider and Binder (`crawbook/`)
- **Required Order**:
  1. Run `python list_spider.py` to generate chapter listings in `chapters.json`.
  2. Run `python content_spider.py` to incrementally download chapters into `content/` (supports auto-resume).
  3. Run `python book_binder.py` to combine downloaded single files into bound `.txt` volumes of 500 chapters each.

### 4. Anki Word Generator (`anki/`)
- **Workflow**: Reads a target CSV list and queries `gemini-2.0-flash` to append metadata (IPA, example sentences, mnemonics).
- **Behavior**: Saves incrementally to avoid progress loss if API quotas are exhausted. Can safely resume from partial runs.
