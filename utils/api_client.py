import os
import requests
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv("BASE_URL", "https://madhavis-academy.evalytics.in")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def set_auth_token(self, token: str):
        """Sets Bearer token or authorization headers."""
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get(self, endpoint, **kwargs):
        return self.session.get(f"{self.base_url}{endpoint}", **kwargs)

    def post(self, endpoint, data=None, json=None, **kwargs):
        return self.session.post(f"{self.base_url}{endpoint}", data=data, json=json, **kwargs)