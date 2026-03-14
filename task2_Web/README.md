# Task 2 – Web Automation (RocScience Login Navigation)

Automated end-to-end test that navigates [rocscience.com](https://rocscience.com), clicks the user/profile icon, selects **"Log in to RocPortal"**, and validates the resulting login page.

## Tech Stack

| Component | Choice |
|-----------|--------|
| Language | Python 3.14 |
| Test Framework | [Pytest](https://docs.pytest.org/) |
| Automation Framework | [Playwright for Python](https://playwright.dev/python/) (Sync API) |
| Assertion Style | Playwright's built-in `expect()` auto-retry assertions |

### Why Playwright?

- **Auto-waiting** – Every action (`click`, `fill`, assertion) waits for the element to be actionable, removing the need for brittle `time.sleep()` calls.
- **Reliable selectors** – CSS, role-based, and text-based locators with automatic retry logic.
- **Cross-browser** – Same test can run on Chromium, Firefox, and WebKit with a single flag.
- **Built-in tracing** – Screenshots, videos, and trace files can be captured on failure for debugging.

---

## Project Structure

```
task2_Web/
├── conftest.py               # Playwright session fixtures (viewport, slow_mo)
├── requirements.txt          # Python dependencies
├── test_web_automation.py    # Main test file
└── README.md                 # This file
```

---

## Prerequisites

- **Python 3.10+** installed
- **pip** (comes with Python)
- A virtual environment is recommended

---

## Setup Instructions

### 1. Create & activate a virtual environment (optional but recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright browsers

```bash
playwright install chromium
```

> This downloads the Chromium browser binary managed by Playwright (~150 MB).

---

## How to Run the Web Test

### Run in headed mode (browser visible) with verbose output

```bash
pytest test_web_automation.py --headed -s
```

### Run in headless mode (CI-friendly, no browser window)

```bash
pytest test_web_automation.py
```

### Run on a specific browser

```bash
pytest test_web_automation.py --headed --browser firefox
pytest test_web_automation.py --headed --browser webkit
```

---

## What the Test Validates

The test `test_rocscience_login_navigation` performs the following steps and validations:

| Step | Action | Validation |
|------|--------|------------|
| 1 | Navigate to `https://rocscience.com` | Page loads successfully |
| 2 | Dismiss cookie banner (if present) | Smart conditional handling |
| 3 | Click the user/profile icon (`#topnav-portal-account-icon`) | Icon is visible before clicking |
| 4 | Click **"Log in to RocPortal"** in the dropdown | Dropdown menu item is found |
| 5 | Validate URL | URL contains `/login` |
| 6 | Validate Email field | `input[type="email"]` or `input[name="username"]` is visible |
| 7 | Validate Password field | `input[type="password"]` or `input[name="password"]` is visible |
| 8 | Validate Login button | Button with `data-action-button-primary="true"` is visible **and enabled** |

---

## Test Execution Evidence

```
===== test session starts ======
platform win32 -- Python 3.14.1, pytest-8.0.0, pluggy-1.6.0
plugins: anyio-4.12.1, base-url-2.1.0, playwright-0.7.2
collected 1 item

test_web_automation.py
[1] Navigating to https://rocscience.com...
[2] Clicking the User/Profile icon...
[3] Clicking 'Log in to RocPortal' option...
[4] Validating Login Page requirements...
    ✅ URL validation passed (contains '/login').
    ✅ Email and Password fields are visible.
    ✅ Login button ('Continue') is visible and enabled.
.

===== 1 passed in 8.24s =====
```

---

## Stability & Design Decisions

1. **No hard sleeps** – All waits use Playwright's built-in auto-wait mechanism (`wait_for`, `expect()`). No `time.sleep()` is used anywhere.
2. **Cookie banner handling** – The test checks for the cookie consent banner and dismisses it if visible, preventing it from blocking interactions.
3. **Resilient selectors** – Multiple selector strategies are used (CSS type selectors + name attributes) to handle potential DOM variations.
4. **Readable output** – Step-by-step `print()` statements provide clear feedback on test progress without requiring report tooling.
5. **Session-level fixtures** – `conftest.py` centralizes browser configuration (viewport size, `slow_mo` for visual stability).

---

## Task 2B – API Thinking for Invalid Login

### 1. Endpoint Discovery

Using the browser's **DevTools → Network tab**, submit a login form and filter by `XHR/Fetch` requests. The login API is typically:

```
POST https://auth.rocscience.com/oauth/token
```

or a similar Auth0-based endpoint (since the login page uses Auth0).

### 2. Example Request Payload

```json
{
  "grant_type": "password",
  "client_id": "<auth0_client_id>",
  "username": "invalid@example.com",
  "password": "WrongPassword123!",
  "audience": "https://api.rocscience.com",
  "scope": "openid profile email"
}
```

### 3. Expected Failure Response

| Signal            | Value                                     |
|-------------------|-------------------------------------------|
| HTTP Status Code  | `401 Unauthorized` or `403 Forbidden`     |
| Response Body     | `{"error": "invalid_grant", "error_description": "Wrong email or password."}` |
| Token             | **Not present** in response               |

### 4. Code Snippet – Python (requests)

```python
import requests

def test_invalid_login_api():
    url = "https://auth.rocscience.com/oauth/token"
    payload = {
        "grant_type": "password",
        "client_id": "YOUR_CLIENT_ID",
        "username": "invalid@example.com",
        "password": "WrongPassword123!",
        "audience": "https://api.rocscience.com",
        "scope": "openid profile email"
    }

    response = requests.post(url, json=payload)

    # Assert login failed
    assert response.status_code in (401, 403), \
        f"Expected 401/403, got {response.status_code}"

    body = response.json()
    assert "error" in body, "Expected error field in response"
    assert body["error"] == "invalid_grant"
    assert "access_token" not in body, "Token should NOT be present"
```

---

## License

This project is submitted as part of a take-home assignment for evaluation purposes only.
