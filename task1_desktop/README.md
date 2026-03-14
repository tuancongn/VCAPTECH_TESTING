# Task 1 – Desktop Automation (Windows Notepad)

Automate a simple workflow in Windows Notepad using Python and [pywinauto](https://pywinauto.readthedocs.io/).

## What It Does

1. **Launch** Notepad
2. **Type** text: `"Desktop automation test"`
3. **Append** text: `" – completed"`
4. **Save** the file to disk
5. *(Bonus)* **Reopen & verify** — reads the saved file and asserts content matches

## Requirements

- **OS**: Windows 10 / 11
- **Python**: 3.10+
- **Dependencies**: see `requirements.txt`

## Setup

```bash
# Activate your virtual environment
.\venv\Scripts\activate          # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python notepad_automator.py
```

### Expected Output

```
[1] Launching Notepad...
    Notepad launched successfully.
[2/3] Typing text: 'Desktop automation test'...
[2/3] Typing text: ' – completed'...
[4] Saving file to: ...\vcaptech_automation_test.txt
    File saved successfully.
[*] Closing Notepad...
[Bonus] Verifying content in: ...\vcaptech_automation_test.txt
    ✅ SUCCESS: File content matches expected text.
[*] Cleanup: Test file deleted.
```

## Project Structure

```
task1_desktop/
├── notepad_automator.py   # Main automation script
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Design Decisions

| Concern | Approach |
|---------|----------|
| **Unicode support** (en-dash `–`) | Clipboard paste via PowerShell `Set-Clipboard` + `Ctrl+V` instead of `type_keys()` |
| **Readiness / timing** | `wait('visible ready')` smart waits instead of hard `time.sleep()` |
| **Save As dialog** | `Desktop(backend="win32")` for reliable dialog detection on classic Win10 Notepad |
| **Error handling** | Try/except blocks with descriptive messages at each step; overwrite confirmation safeguard |
| **Code structure** | `NotepadAutomator` class with single-responsibility methods |
