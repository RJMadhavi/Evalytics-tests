'''
	TEST : Configuration File.
	Version -- 3.0
	Date : 09/14/2026
	-------------------------------------------------------------------------
	Updates -- 
	1. Added the HTML Report Hooks & Configuration.
'''
import os
import pytest
from bs4 import BeautifulSoup
from utils.api_client import APIClient
from config import Config

# ==============================================================================
# 1. PYTEST-HTML REPORT HOOKS (Logs, Screenshots, & API Snippets)
# ==============================================================================

def pytest_html_report_title(report):
    """Customize the title displayed at the top of the HTML report."""
    report.title = "Evalytics Test Execution Report"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook executed after each test step. On failure, captures:
    1. Browser Screenshots (if a Playwright/Selenium 'page' fixture is used)
    2. API Response Body / Status Code (if 'api_client' fixture is used)
    3. Captured Standard Console Logs
    """
    outcome = yield
    report = outcome.get_result()
    
    # Execute only during the main test call phase when a test fails
    if report.when == "call" and report.failed:
        extra = getattr(report, "extra", [])
        import pytest_html

        # 1. CAPTURE BROWSER SCREENSHOT (For UI / Playwright Tests)
        if "page" in item.fixturenames:
            page = item.funcargs.get("page")
            if page:
                screenshot_dir = os.path.join("reports", "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                
                # Sanitize filename
                safe_test_name = item.name.replace("/", "_").replace("::", "_")
                file_path = os.path.join(screenshot_dir, f"{safe_test_name}.png")
                
                # Save Playwright screenshot
                page.screenshot(path=file_path)
                
                # Embed image directly into the HTML report
                extra.append(pytest_html.extras.image(file_path))

        # 2. CAPTURE API FAILURE SNIPPET (For Requests / API Tests)
        if "api_client" in item.fixturenames:
            client = item.funcargs.get("api_client")
            if client and hasattr(client, "last_response") and client.last_response:
                res = client.last_response
                res_info = (
                    f"<div style='background-color:#fff0f0; padding:10px; border:1px solid #f5c6cb; border-radius:4px; font-family:monospace;'>"
                    f"<b>Failed URL:</b> {res.url}<br>"
                    f"<b>Status Code:</b> {res.status_code}<br>"
                    f"<b>Response Body:</b><br><pre>{res.text[:500]}</pre>"
                    f"</div>"
                )
                extra.append(pytest_html.extras.html(res_info))

        # 3. CAPTURE TERMINAL / STDOUT LOGS
        if report.capstdout:
            logs_html = (
                f"<div style='background-color:#f8f9fa; padding:10px; border:1px solid #dee2e6; border-radius:4px; font-family:monospace;'>"
                f"<b>Captured Standard Output / Logs:</b><br><pre>{report.capstdout}</pre>"
                f"</div>"
            )
            extra.append(pytest_html.extras.html(logs_html))

        report.extra = extra


def pytest_configure(config):
    """Add environment metadata to the HTML report header table."""
    if hasattr(config, "_metadata"):
        config._metadata["Project"] = "Evalytics Automation"
        config._metadata["Base URL"] = Config.BASE_URL


# ==============================================================================
# 2. SESSION FIXTURES
# ==============================================================================

@pytest.fixture(scope="session")
def api_client():
    client = APIClient(base_url=Config.BASE_URL)

    # 1. GET the login page to initialize the session
    login_url = f"{Config.BASE_URL}{Config.LOGIN_ENDPOINT}"
    login_page = client.session.get(login_url)
    soup = BeautifulSoup(login_page.text, "html.parser")

    # 2. Extract CSRF Token
    csrf_input = soup.find("input", {"name": "csrf_token"})
    csrf_token = csrf_input.get("value") if csrf_input else ""

    # 3. Payload matching the login form
    login_data = {
        "csrf_token": csrf_token,
        "email": Config.TEACHER_EMAIL,
        "password": Config.TEACHER_PASSWORD,
        "remember": "y"
    }

    # 4. Attach CSRF token to headers & set proper Referer/Origin
    headers = {
        "X-CSRFToken": csrf_token,
        "Referer": login_url,
        "Origin": Config.BASE_URL,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print(f"\n[DEBUG] Logging in with email: '{Config.TEACHER_EMAIL}'")
    print(f"[DEBUG] Session Cookie: {client.session.cookies.get_dict()}")

    # 5. Send POST login request with active cookies preserved
    response = client.session.post(
        login_url,
        data=login_data,
        headers=headers,
        cookies=client.session.cookies,
        allow_redirects=True
    )

    print(f"[DEBUG] Status: {response.status_code} | Final Destination URL: {response.url}")

    # 6. Verify success
    assert (
        "login" not in response.url.lower()
    ), f"Login failed! Still on {response.url} instead of teacher dashboard."

    return client
