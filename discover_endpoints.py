# discover_endpoints.py

from bs4 import BeautifulSoup
from config import Config
from utils.api_client import APIClient


def discover_dashboard_endpoints():
    client = APIClient(base_url=Config.BASE_URL)

    # 1. Fetch login page to establish session & get CSRF token
    login_url = f"{Config.BASE_URL}{Config.LOGIN_ENDPOINT}"
    login_page = client.session.get(login_url)
    soup = BeautifulSoup(login_page.text, "html.parser")

    csrf_input = soup.find("input", {"name": "csrf_token"})
    csrf_token = csrf_input.get("value") if csrf_input else ""

    # 2. Build login payload & headers matching conftest.py
    login_data = {
        "csrf_token": csrf_token,
        "email": Config.TEACHER_EMAIL,
        "password": Config.TEACHER_PASSWORD,
        "remember": "y"
    }

    headers = {
        "X-CSRFToken": csrf_token,
        "Referer": login_url,
        "Origin": Config.BASE_URL,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # 3. Post Login
    login_res = client.session.post(
        login_url,
        data=login_data,
        headers=headers,
        cookies=client.session.cookies,
        allow_redirects=True
    )

    print(f"[DEBUG] Authenticated URL: {login_res.url}")

    if "login" in login_res.url.lower():
        print("❌ Login failed in discovery script! Check credentials.")
        return

    # 4. Fetch Teacher Dashboard Page
    dashboard_url = f"{Config.BASE_URL}/teacher/dashboard"
    dash_res = client.session.get(dashboard_url)
    dash_soup = BeautifulSoup(dash_res.text, "html.parser")

    # 5. Extract all Navigation Links (<a href="...">)
    links = set()
    for tag in dash_soup.find_all("a", href=True):
        href = tag["href"]
        # Filter out external links, anchors, and javascript placeholders
        if not href.startswith("http") or Config.BASE_URL in href:
            if not href.startswith("#") and not href.startswith("javascript:"):
                links.add(href)

    # 6. Extract Form Actions (<form action="...">)
    forms = set()
    for tag in dash_soup.find_all("form", action=True):
        action = tag["action"]
        forms.add(action)

    print("\n================ DISCOVERED DASHBOARD ENDPOINTS ================")
    print("\n--- Authenticated Navigation Pages (GET) ---")
    for link in sorted(links):
        print(f"  GET  -> {link}")

    print("\n--- Form Action Endpoints (POST) ---")
    for action in sorted(forms):
        print(f"  POST -> {action}")
    print("================================================================")


if __name__ == "__main__":
    discover_dashboard_endpoints()