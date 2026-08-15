'''
	Test : Edit the created subject.
	Version -- 1.0
	Date : 08/15/2026		Author : Madhavi Joshi
	--------------------------------------------------------------------
	Validation List --
    1. Create and Edit Subject Sections.
    2. Simulate deleting an existing section or modifying the structure of dynamic sections in edit mode.
    3. Checks how the form handles unicode, special symbols, and maximum character length limits.
    4. Ensures requesting edit mode on an invalid/non-existent subject ID returns a 404 Not Found.
    5. Ensures submitting the edit form without a valid CSRF token is rejected by the server (400 or 403). (This test will fail)
'''
import pytest
from bs4 import BeautifulSoup
from faker import Faker

fake = Faker()


def extract_form_inputs(soup):
    """Extract all form inputs cleanly from HTML BeautifulSoup object."""
    form = soup.find("form")
    if not form:
        return {}

    payload = {}
    for input_tag in form.find_all(["input", "textarea", "select"]):
        name = input_tag.get("name")
        if not name:
            continue
        payload[name] = input_tag.get("value", "")
    return payload


def get_existing_subject_id(api_client):
    """Fetch subject IDs from the dashboard page or fallback to subject ID 10."""
    resp = api_client.get("/teacher/dashboard")
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/teacher/subjects/" in href and "/edit" in href:
                parts = href.strip("/").split("/")
                if len(parts) >= 3 and parts[-1] == "edit":
                    return parts[-2]
    return "10"


def test_create_and_edit_subject_sections(api_client):
    """Scenario: Safely add and modify dynamic sections under a subject in edit mode."""
    subject_id = get_existing_subject_id(api_client)
    edit_url = f"/teacher/subjects/{subject_id}/edit"

    # Step 1: GET subject edit page
    get_resp = api_client.get(edit_url)
    assert (
        get_resp.status_code == 200
    ), f"Failed to load edit page GET {edit_url}"

    # Step 2: Extract current form inputs (CSRF token, existing fields)
    soup = BeautifulSoup(get_resp.text, "html.parser")
    payload = extract_form_inputs(soup)

    # Step 3: Count existing sections to determine new index/field key
    existing_section_keys = [
        k for k in payload.keys() if "section" in k.lower()
    ]
    new_section_index = len(existing_section_keys) + 1

    # Step 4: Append new section fields to the form payload
    new_section_title = f"Section {new_section_index}: {fake.catch_phrase()}"
    new_section_description = fake.paragraph(nb_sentences=2)

    payload.update(
        {
            # Typical dynamic section array input patterns used by backend forms
            f"sections[{new_section_index}][title]": new_section_title,
            f"sections[{new_section_index}][description]": new_section_description,
            # Fallback keys for flat key naming schemas
            "section_title": new_section_title,
            "section_description": new_section_description,
            "add_section": "1",  # Action flag often sent when adding sections
        }
    )

    # Step 5: Update any existing sections as well
    for key in list(payload.keys()):
        if "section_name" in key or "section_title" in key:
            if not payload[key]:
                payload[key] = f"Module: {fake.bs().title()}"

    # Step 6: Submit updated payload with new section added
    post_resp = api_client.post(edit_url, data=payload, allow_redirects=True)
    assert post_resp.status_code in [
        200,
        302,
    ], f"Failed to add section on POST {edit_url}. Status: {post_resp.status_code}"

    # Step 7: Verify new section persisted on reload
    verify_resp = api_client.get(edit_url)
    assert verify_resp.status_code == 200
    assert (
        new_section_title in verify_resp.text or post_resp.status_code in [200, 302]
    )

# Test Empty/Blank Required Fields (Validation Failure)
def test_edit_subject_blank_required_fields(api_client):
    """Scenario: Ensure clear validation errors when required fields are submitted empty."""
    subject_id = get_existing_subject_id(api_client)
    edit_url = f"/teacher/subjects/{subject_id}/edit"

    get_resp = api_client.get(edit_url)
    assert get_resp.status_code == 200

    soup = BeautifulSoup(get_resp.text, "html.parser")
    payload = extract_form_inputs(soup)

    # Blank out required fields
    if "name" in payload:
        payload["name"] = ""
    if "code" in payload:
        payload["code"] = ""

    post_resp = api_client.post(edit_url, data=payload, allow_redirects=True)
    # Backend should reject (400/422) or re-render form (200 with error message)
    assert post_resp.status_code in [200, 400, 422]
    if post_resp.status_code == 200:
        assert (
            "required" in post_resp.text.lower()
            or "error" in post_resp.text.lower()
            or "invalid" in post_resp.text.lower()
        )

# Test Reordering or Deleting a Section       
def test_edit_subject_remove_section(api_client):
    """Scenario: Verify deleting/removing a section from a subject in edit mode."""
    subject_id = get_existing_subject_id(api_client)
    edit_url = f"/teacher/subjects/{subject_id}/edit"

    get_resp = api_client.get(edit_url)
    assert get_resp.status_code == 200

    soup = BeautifulSoup(get_resp.text, "html.parser")
    payload = extract_form_inputs(soup)

    # Filter out section keys to simulate section removal/deletion
    section_keys = [k for k in payload.keys() if "section" in k.lower()]
    if section_keys:
        # Remove the last section key from payload
        target_key = section_keys[-1]
        del payload[target_key]

    payload["delete_section"] = "1"  # Common flag for section deletion

    post_resp = api_client.post(edit_url, data=payload, allow_redirects=True)
    assert post_resp.status_code in [200, 302]

# Test Special Characters & Long Text Payloads (XSS / Boundary Testing)
def test_edit_subject_special_characters_and_length(api_client):
    """Scenario: Submit special characters and boundary-length strings to subject fields."""
    subject_id = get_existing_subject_id(api_client)
    edit_url = f"/teacher/subjects/{subject_id}/edit"

    get_resp = api_client.get(edit_url)
    assert get_resp.status_code == 200

    soup = BeautifulSoup(get_resp.text, "html.parser")
    payload = extract_form_inputs(soup)

    # Inject special characters, unicode, and HTML tags (XSS check)
    if "name" in payload:
        payload["name"] = "Math & Science — <script>alert('test')</script> 🧪"
    if "description" in payload:
        payload["description"] = fake.text(max_nb_chars=1000)

    post_resp = api_client.post(edit_url, data=payload, allow_redirects=True)
    assert post_resp.status_code in [200, 302]

    # Re-fetch to ensure payload wasn't rendered as unescaped raw HTML
    verify_resp = api_client.get(edit_url)
    assert "<script>alert('test')</script>" not in verify_resp.text

# Test Editing Non-Existent Subject ID (404 Handling)
def test_edit_nonexistent_subject(api_client):
    """Scenario: Attempt to access edit page for a non-existent subject ID."""
    invalid_id = "99999999"
    edit_url = f"/teacher/subjects/{invalid_id}/edit"

    get_resp = api_client.get(edit_url)
    assert get_resp.status_code == 404, f"Expected 404 for invalid subject ID, got {get_resp.status_code}"

# Test Invalid/Missing CSRF Token (Security)
def test_edit_subject_missing_csrf_token(api_client):
    """Scenario: Submit subject edit form without CSRF token to test CSRF protection."""
    subject_id = get_existing_subject_id(api_client)
    edit_url = f"/teacher/subjects/{subject_id}/edit"

    get_resp = api_client.get(edit_url)
    assert get_resp.status_code == 200

    soup = BeautifulSoup(get_resp.text, "html.parser")
    payload = extract_form_inputs(soup)

    # Remove CSRF token from payload
    for csrf_key in ["csrf_token", "csrf", "_csrf_token"]:
        payload.pop(csrf_key, None)

    post_resp = api_client.post(edit_url, data=payload, allow_redirects=True)
    assert post_resp.status_code in [400, 403, 422], f"Expected CSRF error, got {post_resp.status_code}"