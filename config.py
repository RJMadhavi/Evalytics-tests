import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

class Config:
    BASE_URL = os.getenv("BASE_URL", "https://madhavis-academy.evalytics.in")
    LOGIN_ENDPOINT = os.getenv("LOGIN_ENDPOINT", "/login")
    TEACHER_EMAIL = os.getenv("TEACHER_EMAIL")
    TEACHER_PASSWORD = os.getenv("TEACHER_PASSWORD")