'''
	Test : Test the Teacher Subjecs page API end points. User should be able to
		add subjects. Delete subjects.
	Version -- 1.0
	Date : 08/14/2026			Author -- Madhavi Joshi
	--------------------------------------------------------------------------
	Updates --
'''

import pytest
from bs4 import BeautifulSoup

def test_teacher_subjects_page_accessible(api_client):
    """Verify that an authenticated teacher can view the subjects list page."""
    response = api_client.get("/teacher/subjects")
    
    # Verify HTTP 200 OK
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Verify page content
    assert "text/html" in response.headers.get("Content-Type", "")
    assert "Subjects" in response.text or "Subject List" in response.text


def test_teacher_create_subject_page_accessible(api_client):
    """Verify that the GET request to load the 'New Subject' form returns HTTP 200 and has the form."""
    response = api_client.get("/teacher/subjects/new")
    
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert "text/html" in response.headers.get("Content-Type", "")
    
    # Ensure the CSRF token hidden input exists on the new subject form
    soup = BeautifulSoup(response.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf_token"})
    assert csrf_input is not None, "CSRF token input field missing on /teacher/subjects/new form page"


def test_create_subject_success(api_client):
    """
    Verify creating a new subject by:
    1. GET /teacher/subjects/new to extract fresh form CSRF token
    2. POST data to create subject
    3. Assert redirection or success and check subject appears on /teacher/subjects
    """
    new_subject_url = "/teacher/subjects/new"
    
    # Step 1: GET form page & extract CSRF token
    form_response = api_client.get(new_subject_url)
    assert form_response.status_code == 200, "Failed to load subject creation form"
    
    soup = BeautifulSoup(form_response.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf_token"})
    csrf_token = csrf_input.get("value") if csrf_input else ""
    
    # Dynamic subject test data
    subject_name = "Automation Testing 101"
    subject_code = "AT-101"
    
    payload = {
        "csrf_token": csrf_token,
        "name": subject_name,
        "code": subject_code,
        "description": "Created via Automated Pytest Suite"
    }
    
    headers = {
        "X-CSRFToken": csrf_token,
        "Referer": f"{api_client.base_url}{new_subject_url}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Step 2: POST to create subject
    post_response = api_client.post(
        new_subject_url,
        data=payload,
        headers=headers,
        allow_redirects=True
    )
    
    # Verify creation request succeeded (Status 200 after redirect follow)
    assert post_response.status_code == 200, f"Failed to submit new subject form. Status: {post_response.status_code}"
    
    # Step 3: Verify created subject is visible on the subjects list page
    list_response = api_client.get("/teacher/subjects")
    assert list_response.status_code == 200
    assert subject_name in list_response.text, f"Subject '{subject_name}' was not found on /teacher/subjects list!"


def test_unauthorized_subjects_access():
    """Verify unauthenticated users cannot access /teacher/subjects or /teacher/subjects/new."""
    from utils.api_client import APIClient
    unauth_client = APIClient()
    
    # Don't follow redirects to catch 302 Redirect to /login or HTTP 401/403
    resp_list = unauth_client.get("/teacher/subjects", allow_redirects=False)
    assert resp_list.status_code in [302, 303, 401, 403], f"Unexpected status code for unauth list: {resp_list.status_code}"

    resp_new = unauth_client.get("/teacher/subjects/new", allow_redirects=False)
    assert resp_new.status_code in [302, 303, 401, 403], f"Unexpected status code for unauth new form: {resp_new.status_code}"
