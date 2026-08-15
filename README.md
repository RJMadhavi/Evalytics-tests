Welcome to Evalytics-tests, a comprehensive testing and validation suite designed for the Evalytics ecosystem. This repository contains automated unit, integration, and performance validation scripts to ensure evaluation pipelines run seamlessly.

🔌 Plug-and-Play Capabilities
This test suite is designed for seamless integration, with a few environment-specific considerations:

Decoupled Architecture: Tests utilize offline mock fixtures stored in the fixtures/ directory by default.

Environment Variables: When connecting to live staging APIs or active Google/Cloud storage schemas used by Evalytics, copy .env.example to .env and fill in your credentials.

Python Runtime: Ensure your local Python environment matches the version required by the core Evalytics implementation (Python 3.9+ recommended) to prevent syntax or typing discrepancies.

🛠️ Repository Structure

```text
Evalytics-tests/
├── tests/
│   ├── __init__.py
│   ├── test_eval_pipeline.py    # Core end-to-end evaluation flow tests
│   ├── test_mapping.py          # Form and schema configuration tests
│   └── test_reports.py          # Output report generation validations
├── fixtures/                    # Mock data files for offline testing
├── config/                      # Test configuration templates
├── requirements.txt             # Python dependencies
└── README.md
```

⚙️ Installation & Setup (Plug & Play)

To set up and run the test suite locally, follow these steps:

### 1. Clone the repository
```bash
git clone [https://github.com/your-username/api-test-suite.git](https://github.com/your-username/api-test-suite.git)
cd api-test-suite
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

🧪 Running the Tests
The tests are structured to run via pytest. To execute the entire plug-and-play test matrix:
```bash
pytest -v
```

To run a specific test module (e.g., pipeline validation):
```bash
pytest tests/test_eval_pipeline.py -v
```

🔌 Are these tests Plug-and-Play?

Yes, with conditions: The tests are designed to be decoupled using mock fixtures located in the fixtures/ directory.
Environment Variables: If you are connecting these tests to live staging APIs or active Google/Cloud storage schemas used by Evalytics, ensure you copy .env.example to .env and configure your credentials accordingly.
Dependencies Check: Ensure that your local Python runtime matches the version required by your main Evalytics implementation (typically Python 3.9+) to prevent syntax or typing mismatches.

📝 Error Checking & Troubleshooting

| Issue | Resolution |
| :--- | ---: |
| Missing Fixtures / File Not Found | Verify that test execution paths resolve correctly to the fixtures/ directory when running isolated tests.
| Dependency Conflicts | Run pip list to check installed package versions against constraints in requirements.txt. |
| Authorization Failures | If integration points are failing, ensure you run in offline mock mode using markers: pytest -m "not integration". | 


🤝 Contributing

Contributions are welcome! Please fork the repository, submit a pull request, or open an issue for any bug fixes or expanded test vectors.
