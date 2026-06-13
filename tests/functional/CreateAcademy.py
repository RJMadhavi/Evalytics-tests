'''
*******************************************************************************************************************************
Author: Madhavi Joshi   Version: 1.0   Date: 2024-05-25
Test Case:  Verify that a user can fill out the Academy registration form,submit it, and see the post-creation confirmation message.

Test Steps:
1. Navigate to the Academy creation page.
2. Fill out the form with valid data: Academy Name, Subdomain, Teacher Name, Email, Password, and Confirm Password.
3. Click the "Create Academy" button.
4. Wait for the page to process the submission and redirect to the confirmation page.
5. Assert that the confirmation page displays the expected heading "Registration Received!".
6. Assert that the dynamic welcome/status string is visible and correctly formatted.
7. Change the database to reflect the Acadmey approval.
8. Login to the Academy and assert that the user can access the dashboard without errors.
*******************************************************************************************************************************
'''
import pytest
import time
from faker import Faker
from playwright.sync_api import Page, expect

# Initialize Faker
fake = Faker()

# Your Docker Compose maps the web service port to 5100
BASE_URL = "http://localhost:5100"

def test_create_academy_with_success_message(page: Page):
    """
    Test Case: Verify that a user can fill out the Academy registration form
    using completely dynamic data and verify the exact matching confirmation details.
    """
    # 1. Generate COMPLETELY dynamic, realistic test data
    teacher_name = fake.name()                       # Generates e.g., "John Doe" or "Madhavi Joshi"
    academy_name = f"{fake.company()} Academy"       # Generates e.g., "Apex Learning Academy"
    email_domain = fake.free_email_domain()           # Generates e.g., "example.com" or "mail.com"
    
    # Keep your unique structural tags to guarantee clean database insertion
    timestamp = int(time.time())
    unique_subdomain = f"academy{timestamp}"
    unique_email = f"qa_{timestamp}@{fake.free_email_domain()}" # Generates a clean random email

    # Step 1: Navigate to the creation page
    page.goto(f"{BASE_URL}/create-academy")
    
    # Step 2: Fill out the actual form inputs using our dynamic variables
    page.fill("input[placeholder='e.g. Shrinath Chemistry Classes']", academy_name)
    page.fill("input[placeholder='shrinathchemistry']", unique_subdomain)
    page.fill("input[placeholder='e.g. Rajesh Kumar']", teacher_name)
    
    page.fill("input[placeholder='you@example.com']", unique_email)
    page.fill("input[placeholder='Min. 8 characters']", "TestPass123!")
    page.fill("input[placeholder='Repeat password']", "TestPass123!")
    
    # Step 3: Click the Submit Button
    page.click("button:has-text('Create Academy')")
    
    # Step 4: Handle the redirection and assert the confirmation message
    page.wait_for_load_state("networkidle")
    
    # -------------------------------------------------------------
    # Assertions remain fully dynamic! They match whatever Faker generated.
    # -------------------------------------------------------------
    
    # 1. Assert the main heading is visible
    expect(page.get_by_role("heading", name="Registration Received!")).to_be_visible()
    
    # 2. Assert the dynamic welcome string using the variables
    expected_status_text = f"Thanks, {teacher_name}. Your academy {academy_name} has been registered and is awaiting approval."
    expect(page.get_by_text(expected_status_text)).to_be_visible()
    
    # 3. Assert the dynamic email mapping inside the instruction card
    expected_instruction_text = f"2. You'll receive a confirmation email at {unique_email} once approved."
    expect(page.get_by_text(expected_instruction_text)).to_be_visible()
    
    # 4. Mask the changing fields for the layout screenshot
    page.screenshot(
        path="tests/screenshots/Registration_Received_Dynamic.png", 
        full_page=True,
        mask=[
            page.get_by_text(teacher_name),
            page.get_by_text(academy_name),
            page.get_by_text(unique_email)
        ]
    )
