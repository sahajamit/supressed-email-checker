import pytest
import json
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Import the application components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from services import SuppressionService, OllamaService
from config import config

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def sample_suppressed_emails():
    """Sample suppressed emails data for testing"""
    return {
        "SuppressedDestinationSummaries": [
            {
                "EmailAddress": "test.complaint@example.com",
                "Reason": "COMPLAINT",
                "LastUpdateTime": "2024-01-15T10:30:00Z"
            },
            {
                "EmailAddress": "test.bounce@example.com",
                "Reason": "BOUNCE",
                "LastUpdateTime": "2024-01-20T14:45:30Z"
            },
            {
                "EmailAddress": "test.unsubscribe@example.com",
                "Reason": "UNSUBSCRIBE",
                "LastUpdateTime": "2024-02-01T09:15:45Z"
            },
            {
                "EmailAddress": "test.reputation@example.com",
                "Reason": "REPUTATION",
                "LastUpdateTime": "2024-02-10T16:22:33Z"
            }
        ]
    }

@pytest.fixture
def temp_json_file(sample_suppressed_emails):
    """Create a temporary JSON file with test data"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_suppressed_emails, f)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    os.unlink(temp_file_path)

@pytest.fixture
def mock_ollama_service():
    """Mock Ollama service for testing"""
    mock_service = Mock(spec=OllamaService)
    mock_service.generate_human_explanation.return_value = "Test explanation from AI"
    return mock_service

@pytest.fixture
def suppression_service_with_test_data(temp_json_file):
    """Create a SuppressionService with test data"""
    with patch.object(config, 'SUPPRESSED_EMAILS_JSON_PATH', temp_json_file):
        service = SuppressionService()
        return service
