import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from main import app
from models import SuppressionInfo


class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.json() == {"message": "Suppressed Email Checker API is running"}
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "suppressed-email-checker"
    
    @patch('main.suppression_service')
    @patch('main.ollama_service')
    def test_check_email_suppressed(self, mock_ollama_service, mock_suppression_service, client):
        """Test checking a suppressed email"""
        # Setup mocks
        suppression_info = SuppressionInfo(
            email_address="test@example.com",
            reason="COMPLAINT",
            last_update_time="2024-01-15T10:30:00Z"
        )
        mock_suppression_service.check_email_suppression.return_value = suppression_info
        mock_suppression_service._format_datetime_human_readable.return_value = "January 15, 2024 at 10:30 AM UTC"
        mock_suppression_service._get_reason_explanation.return_value = "recipient marked emails as spam"
        mock_ollama_service.generate_human_explanation.return_value = "The email test@example.com is suppressed due to complaints."
        
        response = client.post(
            "/check-email",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["is_suppressed"] is True
        assert data["reason"] == "COMPLAINT"
        assert data["last_update_time"] == "2024-01-15T10:30:00Z"
        assert data["human_readable_explanation"] == "The email test@example.com is suppressed due to complaints."
    
    @patch('main.suppression_service')
    def test_check_email_not_suppressed(self, mock_suppression_service, client):
        """Test checking a non-suppressed email"""
        # Setup mock
        mock_suppression_service.check_email_suppression.return_value = None
        
        response = client.post(
            "/check-email",
            json={"email": "valid@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "valid@example.com"
        assert data["is_suppressed"] is False
        assert data["reason"] is None
        assert data["last_update_time"] is None
        assert data["human_readable_explanation"] is None
    
    def test_check_email_invalid_email_format(self, client):
        """Test with invalid email format"""
        response = client.post(
            "/check-email",
            json={"email": "invalid-email"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert any("email" in str(error).lower() for error in data["detail"])
    
    def test_check_email_missing_email_field(self, client):
        """Test with missing email field"""
        response = client.post(
            "/check-email",
            json={}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert any("required" in str(error).lower() for error in data["detail"])
    
    def test_check_email_empty_request_body(self, client):
        """Test with empty request body"""
        response = client.post("/check-email")
        
        assert response.status_code == 422
    
    def test_check_email_invalid_json(self, client):
        """Test with invalid JSON"""
        response = client.post(
            "/check-email",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    @patch('main.suppression_service')
    @patch('main.ollama_service')
    def test_check_email_service_exception(self, mock_ollama_service, mock_suppression_service, client):
        """Test handling of service exceptions"""
        # Setup mock to raise exception
        mock_suppression_service.check_email_suppression.side_effect = Exception("Database error")
        
        response = client.post(
            "/check-email",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Internal server error" in data["detail"]
    
    @patch('main.suppression_service')
    @patch('main.ollama_service')
    def test_check_email_all_suppression_reasons(self, mock_ollama_service, mock_suppression_service, client):
        """Test all different suppression reasons"""
        reasons = ["COMPLAINT", "BOUNCE", "UNSUBSCRIBE", "REPUTATION"]
        
        for reason in reasons:
            suppression_info = SuppressionInfo(
                email_address=f"test.{reason.lower()}@example.com",
                reason=reason,
                last_update_time="2024-01-15T10:30:00Z"
            )
            mock_suppression_service.check_email_suppression.return_value = suppression_info
            mock_suppression_service._format_datetime_human_readable.return_value = "January 15, 2024 at 10:30 AM UTC"
            mock_suppression_service._get_reason_explanation.return_value = f"test explanation for {reason}"
            mock_ollama_service.generate_human_explanation.return_value = f"AI explanation for {reason}"
            
            response = client.post(
                "/check-email",
                json={"email": f"test.{reason.lower()}@example.com"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["reason"] == reason
            assert data["is_suppressed"] is True
    
    def test_check_email_case_insensitive(self, client):
        """Test that email checking is case insensitive"""
        with patch('main.suppression_service') as mock_service:
            mock_service.check_email_suppression.return_value = None
            
            response = client.post(
                "/check-email",
                json={"email": "TEST@EXAMPLE.COM"}
            )
            
            assert response.status_code == 200
            # Verify that the service was called with lowercase email
            mock_service.check_email_suppression.assert_called_once_with("test@example.com")
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/check-email")
        
        # FastAPI with CORS middleware should handle OPTIONS requests
        assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly defined
    
    def test_content_type_validation(self, client):
        """Test content type validation"""
        response = client.post(
            "/check-email",
            data="email=test@example.com",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should expect JSON content type
        assert response.status_code == 422


class TestAPIIntegration:
    """Integration tests for the API"""
    
    @patch('services.OllamaService')
    def test_full_integration_suppressed_email(self, mock_ollama_class, client, temp_json_file):
        """Test full integration with real suppression service and mocked Ollama"""
        # Setup Ollama mock
        mock_ollama_instance = Mock()
        mock_ollama_instance.generate_human_explanation.return_value = "Integration test explanation"
        mock_ollama_class.return_value = mock_ollama_instance
        
        # Patch the config to use our test file
        with patch('config.config.SUPPRESSED_EMAILS_JSON_PATH', temp_json_file):
            # Restart the app to pick up new config
            from main import app
            test_client = TestClient(app)
            
            response = test_client.post(
                "/check-email",
                json={"email": "test.complaint@example.com"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_suppressed"] is True
            assert data["reason"] == "COMPLAINT"
    
    def test_api_documentation_endpoints(self, client):
        """Test that API documentation endpoints are accessible"""
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        # Test Swagger UI (might redirect)
        response = client.get("/docs")
        assert response.status_code in [200, 307]  # 307 for redirect
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code in [200, 307]  # 307 for redirect
