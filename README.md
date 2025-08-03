# Suppressed Email Checker API

A FastAPI-based service that checks if email addresses are suppressed and provides human-readable explanations using Ollama AI.

## Features

- ✅ Check email suppression status via REST API
- ✅ Returns detailed suppression information (reason, last update time)
- ✅ AI-powered human-readable explanations using Ollama
- ✅ Configurable JSON data source
- ✅ FastAPI with automatic API documentation
- ✅ CORS support for web applications

## Prerequisites

- Python 3.8+
- Ollama installed and running locally
- Ollama model `qwen2.5:8b` (or configure your preferred model)

## Installation

1. Clone or navigate to the project directory:
```bash
cd supressed-email-checker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure Ollama is running with the required model:
```bash
# Start Ollama (if not already running)
ollama serve

# Pull the model (if not already available)
ollama pull qwen2.5:8b
```

## Configuration

### Environment Variables

The service can be configured using environment variables or by modifying the `config.py` file:

| Variable | Description | Default Value | Example |
|----------|-------------|---------------|----------|
| `SUPPRESSED_EMAILS_JSON_PATH` | Path to JSON file with suppressed emails data | `suppressed_emails.json` | `/path/to/my/emails.json` |
| `OLLAMA_MODEL` | Ollama model to use for generating explanations | `qwen3:8b` | `llama3:8b`, `mistral:7b` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` | `http://192.168.1.100:11434` |
| `API_HOST` | API server host address | `0.0.0.0` | `localhost`, `127.0.0.1` |
| `API_PORT` | API server port | `8000` | `3000`, `5000` |

### Setting Environment Variables

**On macOS/Linux:**
```bash
export SUPPRESSED_EMAILS_JSON_PATH="/path/to/your/emails.json"
export OLLAMA_MODEL="llama3:8b"
export API_PORT="3000"
python3 main.py
```

**Using a .env file (create `.env` in project root):**
```env
SUPPRESSED_EMAILS_JSON_PATH=/path/to/your/emails.json
OLLAMA_MODEL=llama3:8b
OLLAMA_BASE_URL=http://localhost:11434
API_HOST=0.0.0.0
API_PORT=8000
```

**On Windows:**
```cmd
set SUPPRESSED_EMAILS_JSON_PATH=C:\path\to\your\emails.json
set OLLAMA_MODEL=llama3:8b
set API_PORT=3000
python main.py
```

### Ollama Model Configuration

The service uses Ollama for generating human-readable explanations. Supported models include:

- `qwen3:8b` (default) - Fast and accurate
- `llama3:8b` - Good general performance
- `mistral:7b` - Lightweight option
- `deepseek-r1` - Advanced reasoning (supports thinking mode)

**To install a different model:**
```bash
# List available models
ollama list

# Pull a new model
ollama pull llama3:8b

# Set the model in environment
export OLLAMA_MODEL="llama3:8b"
```

## Running the Service

### Quick Start

1. **Start the service:**
   ```bash
   python3 main.py
   ```
   
2. **The API will be available at:** `http://localhost:8000`

### Alternative Run Methods

#### Using Uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### With auto-reload for development:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Running on a different port:
```bash
# Method 1: Environment variable
export API_PORT=3000
python3 main.py

# Method 2: Direct uvicorn
uvicorn main:app --host 0.0.0.0 --port 3000
```

#### Running with custom configuration:
```bash
# Set environment variables and run
export SUPPRESSED_EMAILS_JSON_PATH="/path/to/your/emails.json"
export OLLAMA_MODEL="llama3:8b"
export API_PORT="3000"
python3 main.py
```

### Background/Production Mode

#### Using nohup (runs in background):
```bash
nohup python3 main.py > app.log 2>&1 &
```

#### Using screen (detachable session):
```bash
screen -S email-checker
python3 main.py
# Press Ctrl+A, then D to detach
# To reattach: screen -r email-checker
```

### Stopping the Service

- **If running in foreground:** Press `Ctrl+C`
- **If running in background:** 
  ```bash
  # Find the process ID
  ps aux | grep "python3 main.py"
  
  # Kill the process (replace PID with actual process ID)
  kill <PID>
  ```

### Verifying the Service is Running

```bash
# Check if the service responds
curl http://localhost:8000/health

# Expected response: {"status":"healthy","service":"suppressed-email-checker"}
```

## API Documentation

Once running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

### Check Email Suppression
```bash
curl -X POST "http://localhost:8000/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "recipient2@example.com"}'
```

## Curl Command Examples

### Basic API Testing

#### 1. Health Check
```bash
curl -X GET "http://localhost:8000/health"
```
**Response:**
```json
{"status":"healthy","service":"suppressed-email-checker"}
```

#### 2. Root Endpoint
```bash
curl -X GET "http://localhost:8000/"
```
**Response:**
```json
{"message":"Suppressed Email Checker API is running"}
```

### Email Suppression Checking

#### 3. Check Suppressed Email (COMPLAINT Reason)
```bash
curl -X POST "http://localhost:8000/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "recipient2@example.com"}'
```
**Response:**
```json
{
  "email": "recipient2@example.com",
  "is_suppressed": true,
  "reason": "COMPLAINT",
  "last_update_time": "2020-04-10T21:03:05Z",
  "human_readable_explanation": "The email address recipient2@example.com is suppressed because the recipient marked emails from this sender as spam or complained about receiving them. This suppression was last updated on April 10, 2020 at 09:03 PM UTC."
}
```

#### 4. Check Suppressed Email (BOUNCE Reason)
```bash
curl -X POST "http://localhost:8000/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "recipient1@example.com"}'
```
**Response:**
```json
{
  "email": "recipient1@example.com",
  "is_suppressed": true,
  "reason": "BOUNCE",
  "last_update_time": "2020-04-10T22:07:59Z",
  "human_readable_explanation": "The email address recipient1@example.com is suppressed because emails to this address consistently bounce back, indicating the email address may be invalid or the mailbox is full. This suppression was last updated on April 10, 2020 at 10:07 PM UTC."
}
```

#### 5. Check Another Suppressed Email (COMPLAINT Reason)
```bash
curl -X POST "http://localhost:8000/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "recipient0@example.com"}'
```
**Response:**
```json
{
  "email": "recipient0@example.com",
  "is_suppressed": true,
  "reason": "COMPLAINT",
  "last_update_time": "2020-04-10T21:04:26Z",
  "human_readable_explanation": "The email address recipient0@example.com is suppressed because the recipient marked emails from this sender as spam or complained about receiving them. This suppression was last updated on April 10, 2020 at 09:04 PM UTC."
}
```

#### 6. Check Non-Suppressed Email
```bash
curl -X POST "http://localhost:8000/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "valid@example.com"}'
```
**Response:**
```json
{
  "email": "valid@example.com",
  "is_suppressed": false,
  "reason": null,
  "last_update_time": null,
  "human_readable_explanation": null
}
```

### Advanced curl Examples

#### 7. Pretty Print JSON Response (using jq)
```bash
curl -X POST "http://localhost:8000/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "recipient2@example.com"}' | jq
```

#### 8. Save Response to File
```bash
curl -X POST "http://localhost:8000/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "recipient2@example.com"}' \
     -o response.json
```

#### 9. Check Multiple Emails (Batch Script)
```bash
#!/bin/bash
emails=("recipient0@example.com" "recipient1@example.com" "recipient2@example.com" "valid@example.com")

for email in "${emails[@]}"; do
    echo "Checking: $email"
    curl -X POST "http://localhost:8000/check-email" \
         -H "Content-Type: application/json" \
         -d "{\"email\": \"$email\"}" | jq
    echo "---"
done
```

#### 10. Test with Different API Port
```bash
# If running on port 3000
curl -X POST "http://localhost:3000/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "recipient2@example.com"}'
```

#### 11. Test with Remote Server
```bash
# If API is running on a remote server
curl -X POST "http://192.168.1.100:8000/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "recipient2@example.com"}'
```

#### 12. Include Response Headers
```bash
curl -X POST "http://localhost:8000/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "recipient2@example.com"}' \
     -i
```

#### 13. Verbose Output for Debugging
```bash
curl -X POST "http://localhost:8000/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "recipient2@example.com"}' \
     -v
```

### Error Testing

#### 14. Test Invalid Email Format
```bash
curl -X POST "http://localhost:8000/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "invalid-email"}'
```
**Expected Response:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "invalid-email"
    }
  ]
}
```

#### 15. Test Missing Email Field
```bash
curl -X POST "http://localhost:8000/check-email" \
     -H "Content-Type: application/json" \
     -d '{}'
```
**Expected Response:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

## Data Format

The service reads suppressed email data from a JSON file with the following structure:

```json
{
    "SuppressedDestinationSummaries": [
        {
            "EmailAddress": "recipient2@example.com",
            "Reason": "COMPLAINT",
            "LastUpdateTime": "2020-04-10T21:03:05Z"
        },
        {
            "EmailAddress": "recipient0@example.com",
            "Reason": "COMPLAINT",
            "LastUpdateTime": "2020-04-10T21:04:26Z"
        },
        {
            "EmailAddress": "recipient1@example.com",
            "Reason": "BOUNCE",
            "LastUpdateTime": "2020-04-10T22:07:59Z"
        }
    ]
}
```

### Customizing Your JSON Data File

To use your own suppressed emails data:

1. **Create your JSON file** with the same structure as above
2. **Set the path** using environment variable:
   ```bash
   export SUPPRESSED_EMAILS_JSON_PATH="/path/to/your/data.json"
   ```
3. **Ensure proper format** - each entry must have:
   - `EmailAddress`: Valid email address
   - `Reason`: Suppression reason (COMPLAINT, BOUNCE, UNSUBSCRIBE, REPUTATION)
   - `LastUpdateTime`: ISO 8601 datetime string

### Example Custom JSON File

```json
{
    "SuppressedDestinationSummaries": [
        {
            "EmailAddress": "user1@company.com",
            "Reason": "UNSUBSCRIBE",
            "LastUpdateTime": "2024-01-15T10:30:00Z"
        },
        {
            "EmailAddress": "user2@company.com",
            "Reason": "REPUTATION",
            "LastUpdateTime": "2024-01-20T14:45:30Z"
        },
        {
            "EmailAddress": "bounced@invalid-domain.com",
            "Reason": "BOUNCE",
            "LastUpdateTime": "2024-02-01T09:15:45Z"
        }
    ]
}
```
```

## Suppression Reasons

The API supports the following suppression reasons:

- **COMPLAINT**: Recipient marked emails as spam or complained
- **BOUNCE**: Emails consistently bounce back (invalid address/full mailbox)
- **UNSUBSCRIBE**: Recipient has unsubscribed from emails
- **REPUTATION**: Sender's reputation negatively affected

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid email format
- **500 Internal Server Error**: Server-side issues (file not found, Ollama connection issues, etc.)

## Testing with Different Tools

### Using httpie
```bash
http POST localhost:8000/check-email email=recipient2@example.com
```

### Using Python requests
```python
import requests

response = requests.post(
    "http://localhost:8000/check-email",
    json={"email": "recipient2@example.com"}
)
print(response.json())
```

### Using JavaScript fetch
```javascript
fetch('http://localhost:8000/check-email', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        email: 'recipient2@example.com'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Development

### Project Structure
```
supressed-email-checker/
├── main.py                    # FastAPI application
├── models.py                  # Pydantic models
├── services.py               # Business logic services
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── suppressed_emails.json    # Sample data file
└── README.md                 # This file
```

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check if the model is available: `ollama list`
- Verify the model name in config matches your installed model

### JSON File Issues
- Ensure the JSON file exists at the configured path
- Verify the JSON structure matches the expected format
- Check file permissions

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process if needed
kill -9 <PID>
```

## Testing

The project includes a comprehensive test suite using pytest to ensure reliability and maintainability.

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Test fixtures and configuration
├── test_api.py          # API endpoint tests
├── test_models.py       # Pydantic model tests
└── test_services.py     # Business logic tests
```

### Running Tests

#### Install Test Dependencies
```bash
pip install -r requirements.txt
```

#### Run All Tests
```bash
# Using pytest directly
pytest tests/ -v

# Using the test runner script
python3 run_tests.py

# Make test runner executable and run
chmod +x run_tests.py
./run_tests.py
```

#### Run Specific Tests
```bash
# Test specific file
pytest tests/test_api.py -v

# Test specific class
pytest tests/test_services.py::TestSuppressionService -v

# Test specific function
pytest tests/test_api.py::TestAPIEndpoints::test_check_email_suppressed -v

# Using test runner for specific tests
python3 run_tests.py tests/test_api.py
```

#### Run Tests with Coverage
```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage report
pytest tests/ --cov=. --cov-report=html --cov-report=term

# View HTML coverage report
open htmlcov/index.html
```

### Test Categories

#### Unit Tests
- **Service Tests** (`test_services.py`): Test business logic, data loading, email checking, datetime formatting, and Ollama integration
- **Model Tests** (`test_models.py`): Test Pydantic model validation, serialization, and data integrity
- **API Tests** (`test_api.py`): Test FastAPI endpoints, request/response handling, and error cases

#### Integration Tests
- **Full API Integration**: Test complete request flow with mocked external dependencies
- **Service Integration**: Test interaction between suppression service and Ollama service

### Test Features

✅ **Comprehensive Coverage**
- All API endpoints (/, /health, /check-email)
- All suppression reasons (COMPLAINT, BOUNCE, UNSUBSCRIBE, REPUTATION)
- Error handling and edge cases
- Input validation and sanitization

✅ **Mocking Strategy**
- Ollama service mocked to avoid external dependencies
- Temporary test data files for isolation
- Service-level mocking for unit tests

✅ **Test Data**
- Sample suppressed emails with all reason types
- Invalid email formats for validation testing
- Edge cases and error conditions

### Example Test Output

```bash
$ python3 run_tests.py
🧪 Running Suppressed Email Checker Tests
==================================================
📦 Installing test dependencies...

🔍 Running tests...
tests/test_api.py::TestAPIEndpoints::test_root_endpoint PASSED
tests/test_api.py::TestAPIEndpoints::test_health_endpoint PASSED
tests/test_api.py::TestAPIEndpoints::test_check_email_suppressed PASSED
tests/test_api.py::TestAPIEndpoints::test_check_email_not_suppressed PASSED
tests/test_models.py::TestEmailCheckRequest::test_valid_email PASSED
tests/test_models.py::TestEmailCheckRequest::test_invalid_email_no_at PASSED
tests/test_services.py::TestSuppressionService::test_check_email_suppression_found PASSED
tests/test_services.py::TestOllamaService::test_generate_human_explanation_success PASSED

✅ All tests passed!
```

### Continuous Integration

For CI/CD pipelines, you can use:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ -v --tb=short
```

### Test Development

When adding new features:

1. **Write tests first** (TDD approach)
2. **Add test fixtures** in `conftest.py` for reusable test data
3. **Mock external dependencies** (Ollama, file system)
4. **Test both success and failure cases**
5. **Verify error handling and edge cases**

## License

This project is open source and available under the MIT License.
