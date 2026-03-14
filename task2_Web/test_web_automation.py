import re
from playwright.sync_api import Page, expect


def test_rocscience_login_navigation(page: Page):
    """
    Test Case: Verify navigation to RocPortal login page and validate elements.
    Framework: Playwright (Sync API) + Pytest.
    """
    print("\n[1] Navigating to https://rocscience.com...")
    page.goto("https://rocscience.com")

    # --- STEP 1: Handle Cookie Consent Banner ---
    # Wait for the banner to appear (short timeout so test doesn't hang if absent)
    try:
        reject_btn = page.locator("button.iubenda-cs-reject-btn")
        reject_btn.wait_for(state="visible", timeout=5000)
        print("[*] Dismissing Cookie Banner (Clicking 'Reject all')...")
        reject_btn.click()
        # Wait for the banner overlay to fully disappear before proceeding
        page.locator("#iubenda-cs-banner").wait_for(state="hidden", timeout=5000)
    except Exception:
        print("[*] No cookie banner detected, continuing...")

    # --- STEP 2: Click the User/Profile Icon ---
    print("[2] Clicking the User/Profile icon...")
    profile_icon = page.locator("#topnav-portal-account-icon")
    profile_icon.wait_for(state="visible")
    profile_icon.click()

    # --- STEP 3: Click 'Log in to RocPortal' in the dropdown menu ---
    print("[3] Clicking 'Log in to RocPortal' option...")
    login_option = page.locator("div.account-dropdown-row", has_text="Log in to RocPortal")
    login_option.click()

    # --- STEP 4: VALIDATIONS ---
    print("[4] Validating Login Page requirements...")

    # Validate 1: URL contains the login path
    # Uses regex to cover variations like auth.rocscience.com/u/login...
    expect(page).to_have_url(re.compile(r".*/login.*"))
    print("    ✅ URL validation passed (contains '/login').")

    # Validate 2 & 3: Email and Password fields are visible
    # Uses multiple selectors for resilience against Auth0 DOM structure changes
    email_input = page.locator('input[type="email"], input[name="username"]')
    password_input = page.locator('input[type="password"], input[name="password"]')

    expect(email_input).to_be_visible()
    expect(password_input).to_be_visible()
    print("    ✅ Email and Password fields are visible.")

    # Validate 4: Login button is visible and enabled
    # The Auth0 login form uses a "Continue" button with data-action-button-primary="true"
    login_button = page.locator('button[data-action-button-primary="true"]:has-text("Continue")')

    expect(login_button).to_be_visible()
    expect(login_button).to_be_enabled()
    print("    ✅ Login button ('Continue') is visible and enabled.")
