Welcome to Evalytics-tests, a comprehensive testing and validation suite designed for the Evalytics ecosystem. This repository contains automated unit, integration, and performance validation scripts to ensure evaluation pipelines run seamlessly.

🚀 Features

Plug-and-Play Architecture: Modular test suites designed to drop into existing pipelines with minimal configuration.
Automated Evaluation Checks: Validates data input mapping, score calculations, and report generation processes.
Extensible Framework: Easily write custom assertions for specific evaluation cycles.

🛠️ Repository Structure

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
If you run into issues during execution, check for the following common errors:
Missing Fixtures / File Not Found: Ensure your test paths point correctly to the mock directories if running isolated unit tests.
Dependency Conflicts: Run pip list to check package versions against requirements.txt.
Environment Scope: If tests fail on authorization blocks, make sure you are executing them in an offline mock mode (pytest -m "not integration" if markers are configured).

🤝 Contributing
Contributions are welcome! Please fork the repository, submit a pull request, or open an issue for any bug fixes or expanded test vectors.
