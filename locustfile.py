'''
    Author : Madhavi Joshi      Version =2.0        Date = 2024-06-10
    This script is a locust load test for creating multiple academies concurrently. 
    It simulates Load test for creating multiple academies concurrently.
'''

import os
import random
import re

from faker import Faker
from locust import HttpUser, constant_pacing, task

fake = Faker()


class AcademyCreationUser(HttpUser):
    host = os.getenv("LOCUST_HOST", "http://localhost:5100")

    # RPS per user. Default is intentionally conservative so the app's
    # global limiter (500 requests/hour) is not exhausted during a short run.
    rps_per_user = float(os.getenv("LOCUST_RPS_PER_USER", "0.001"))
    wait_time = constant_pacing(1 / rps_per_user)

    @task
    def create_academy(self):
        with self.client.get("/create-academy", catch_response=True) as get_response:
            if get_response.status_code != 200:
                get_response.failure(f"Could not load academy form: {get_response.status_code}")
                return

            csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', get_response.text)
            if not csrf_match:
                get_response.failure("CSRF token missing from academy form")
                return

            token = csrf_match.group(1)

        unique_suffix = random.randint(100000, 999999)
        academy_name = f"{fake.company()} Academy {unique_suffix}"
        subdomain = f"{fake.slug().replace('-', '')}{unique_suffix}".lower()[:60]
        teacher_name = fake.name()
        email = fake.email().lower()
        password = "SecurePassword123!"

        payload = {
            "csrf_token": token,
            "academy_name": academy_name,
            "subdomain": subdomain,
            "teacher_name": teacher_name,
            "email": email,
            "password": password,
            "confirm_password": password,
            "sub_billing": "monthly",
            "sub_teachers": "1",
            "sub_students": "10",
            "sub_modules": "",
            "sub_monthly_price": "0",
            "sub_annual_price": "0",
        }

        with self.client.post("/create-academy", data=payload, catch_response=True) as post_response:
            if post_response.status_code in (200, 302, 303):
                post_response.success()
            else:
                post_response.failure(f"Academy creation failed with status {post_response.status_code}")