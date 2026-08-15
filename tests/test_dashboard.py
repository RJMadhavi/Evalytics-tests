'''
	Test : Login using Teacher credentials and verify that the Dashboard page loads.
	Version -- 1.0
	Date : 08/14/2026
	-----------------------------------------------------------------------------------
	Updates --

'''
import pytest

def test_teacher_dashboard_accessible(api_client):
    """Verify that an authenticated session can successfully access the teacher dashboard."""
    response = api_client.get("/teacher/dashboard")
    
    # Verify HTTP 200 OK
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Verify response contains HTML expected on the dashboard page
    assert "text/html" in response.headers.get("Content-Type", "")
    assert "Dashboard" in response.text or "Logout" in response.text

def test_unauthorized_dashboard_access():
    """Verify that accessing dashboard without logging in redirects or blocks access."""
    from utils.api_client import APIClient
    unauth_client = APIClient()
    
    # Don't follow redirects automatically so we can catch 302 Redirects to /login
    response = unauth_client.get("/teacher/dashboard", allow_redirects=False)
    
    # Standard security behavior for HTML web apps is 302 Redirect to /login, 401, or 403
    assert response.status_code in [302, 303, 401, 403], f"Unexpected status code: {response.status_code}"