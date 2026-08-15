'''
	Test : Test the Teacher Subjects Editing & Section Management API endpoints using Faker.
	Version -- 1.0
	Date : 08/15/2026			Author -- Madhavi Joshi
	--------------------------------------------------------------------------
  Updates --
'''

import re
import pytest
from bs4 import BeautifulSoup
from faker import Faker

# Initialize Faker instance
fake = Faker()


def generate_fake_subject_data():
    """Generates realistic dynamic subject details using Faker."""
    return {
        "name": f"{fake.job()} - {fake.catch_phrase()}",
        "code": f"{fake.lexify(text='???').upper()}-{fake.numerify(text='###')}",
        "description": fake.sentence(nb_words=10)
    }


def get_dynamic_subject_id(api_client):
    """
    Dynamically fetches the /teacher/subjects page and extracts 
    the first available subject ID from edit links.
    Creates a new subject with Faker data if none exists.
    """
    response = api_client.get("/teacher/subjects")
    assert response.status_code == 200, "Failed to load subjects list page"
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Locate links matching '/teacher/subjects/<id>/edit'
    edit_link = soup.find("a", href=re.compile(r"/teacher/subjects/\d+/edit"))
    
    if edit_link:
        match = re.search(r"/teacher/subjects/(\d+)/edit", edit_link["href"])
        if match:
            return match.group(1)
            
    # Fallback: Create a new subject if none are currently present
    new_form_resp = api_client.get("/teacher/subjects/new")
    soup_form = BeautifulSoup(new_form_resp.text, "html.parser")
    csrf_token = soup_form.find("input", {"name": "csrf_token"}).get("value", "")
    
    payload = generate_fake_subject_data()
    payload["csrf_token"] = csrf_token
    
    post_resp = api_client.post("/teacher/subjects/new", data=payload, allow_redirects=True)
    assert post_resp.status_code == 200
    
    soup_updated = BeautifulSoup(api_client.get("/teacher/subjects").text, "html.parser")
    edit_link = soup_updated.find("a", href=re.compile(r"/teacher/subjects/\d+/edit"))
    assert edit_link is not None, "Could not dynamically obtain or create a valid subject ID."
    
    return re.search(r"/teacher/subjects/(\d+)/edit", edit_link["href"]).group(1)


# --- TESTS ---

def test_teacher_edit_subject_page_accessible(api_client):
    """Verify GET /teacher/subjects/{id}/edit returns 200 OK using a dynamic subject ID."""
    subject_id = get_dynamic_subject_id(api_client)
    edit_url = f"/teacher/subjects/{subject_id}/edit"
    
    response = api_client.get(edit_url)
    assert response.status_code == 200, f"Expected 200 OK for edit page, got {response.status_code}"
    
    soup = BeautifulSoup(response.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf_token"})
    assert csrf_input is not None, f"CSRF token missing on {edit_url}"


def test_edit_subject_details_success(api_client):
    """Verify editing subject metadata using Faker-generated values."""
    subject_id = get_dynamic_subject_id(api_client)
    edit_url = f"/teacher/subjects/{subject_id}/edit"
    
    # 1. Fetch edit form to get current CSRF token
    get_resp = api_client.get(edit_url)
    soup = BeautifulSoup(get_resp.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"}).get("value", "")
    
    # 2. Generate updated values using Faker
    fake_data = generate_fake_subject_data()
    payload = {
        "csrf_token": csrf_token,
        "name": fake_data["name"],
        "code": fake_data["code"],
        "description": fake_data["description"]
    }
    
    headers = {
        "X-CSRFToken": csrf_token,
        "Referer": f"{api_client.base_url}{edit_url}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # 3. Post updates
    post_resp = api_client.post(edit_url, data=payload, headers=headers, allow_redirects=True)
    assert post_resp.status_code == 200, f"Failed to submit edit form. Status: {post_resp.status_code}"
    
    # 4. Verify updated subject name appears in response
    assert fake_data["name"] in post_resp.text or fake_data["name"] in api_client.get("/teacher/subjects").text


def test_edit_subject_sections_update(api_client):
    """Verify updating dynamic section names on a subject form."""
    subject_id = get_dynamic_subject_id(api_client)
    edit_url = f"/teacher/subjects/{subject_id}/edit"
    
    get_resp = api_client.get(edit_url)
    soup = BeautifulSoup(get_resp.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"}).get("value", "")
    
    # Generate realistic section names with Faker
    section_1_name = f"Module 1: {fake.bs().title()}"
    section_2_name = f"Module 2: {fake.bs().title()}"
    
    fake_data = generate_fake_subject_data()
    payload = {
        "csrf_token": csrf_token,
        "name": fake_data["name"],
        "code": fake_data["code"],
        "sections[0][name]": section_1_name,
        "sections[1][name]": section_2_name
    }
    
    headers = {
        "X-CSRFToken": csrf_token,
        "Referer": f"{api_client.base_url}{edit_url}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    post_resp = api_client.post(edit_url, data=payload, headers=headers, allow_redirects=True)
    assert post_resp.status_code == 200
    
    soup_post = BeautifulSoup(post_resp.text, "html.parser")
    assert section_1_name in soup_post.get_text(), f"Section '{section_1_name}' was not saved!"
