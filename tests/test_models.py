import pytest
from pydantic import ValidationError

from models import EmailCheckRequest, EmailCheckResponse, SuppressionInfo


class TestEmailCheckRequest:
    """Test cases for EmailCheckRequest model"""
    
    def test_valid_email(self):
        """Test valid email validation"""
        request = EmailCheckRequest(email="test@example.com")
        assert request.email == "test@example.com"
    
    def test_valid_email_with_subdomain(self):
        """Test valid email with subdomain"""
        request = EmailCheckRequest(email="user@mail.example.com")
        assert request.email == "user@mail.example.com"
    
    def test_valid_email_with_plus(self):
        """Test valid email with plus sign"""
        request = EmailCheckRequest(email="user+tag@example.com")
        assert request.email == "user+tag@example.com"
    
    def test_invalid_email_no_at(self):
        """Test invalid email without @ symbol"""
        with pytest.raises(ValidationError) as exc_info:
            EmailCheckRequest(email="invalid-email")
        
        assert "value is not a valid email address" in str(exc_info.value)
    
    def test_invalid_email_no_domain(self):
        """Test invalid email without domain"""
        with pytest.raises(ValidationError) as exc_info:
            EmailCheckRequest(email="user@")
        
        assert "value is not a valid email address" in str(exc_info.value)
    
    def test_invalid_email_no_local_part(self):
        """Test invalid email without local part"""
        with pytest.raises(ValidationError) as exc_info:
            EmailCheckRequest(email="@example.com")
        
        assert "value is not a valid email address" in str(exc_info.value)
    
    def test_empty_email(self):
        """Test empty email"""
        with pytest.raises(ValidationError) as exc_info:
            EmailCheckRequest(email="")
        
        assert "value is not a valid email address" in str(exc_info.value)
    
    def test_missing_email_field(self):
        """Test missing email field"""
        with pytest.raises(ValidationError) as exc_info:
            EmailCheckRequest()
        
        assert "Field required" in str(exc_info.value)


class TestEmailCheckResponse:
    """Test cases for EmailCheckResponse model"""
    
    def test_suppressed_email_response(self):
        """Test response for suppressed email"""
        response = EmailCheckResponse(
            email="test@example.com",
            is_suppressed=True,
            reason="COMPLAINT",
            last_update_time="2024-01-15T10:30:00Z",
            human_readable_explanation="Test explanation"
        )
        
        assert response.email == "test@example.com"
        assert response.is_suppressed is True
        assert response.reason == "COMPLAINT"
        assert response.last_update_time == "2024-01-15T10:30:00Z"
        assert response.human_readable_explanation == "Test explanation"
    
    def test_non_suppressed_email_response(self):
        """Test response for non-suppressed email"""
        response = EmailCheckResponse(
            email="valid@example.com",
            is_suppressed=False
        )
        
        assert response.email == "valid@example.com"
        assert response.is_suppressed is False
        assert response.reason is None
        assert response.last_update_time is None
        assert response.human_readable_explanation is None
    
    def test_response_with_optional_fields_none(self):
        """Test response with optional fields explicitly set to None"""
        response = EmailCheckResponse(
            email="test@example.com",
            is_suppressed=False,
            reason=None,
            last_update_time=None,
            human_readable_explanation=None
        )
        
        assert response.email == "test@example.com"
        assert response.is_suppressed is False
        assert response.reason is None
        assert response.last_update_time is None
        assert response.human_readable_explanation is None
    
    def test_response_serialization(self):
        """Test response model serialization"""
        response = EmailCheckResponse(
            email="test@example.com",
            is_suppressed=True,
            reason="BOUNCE",
            last_update_time="2024-01-15T10:30:00Z",
            human_readable_explanation="Email bounced"
        )
        
        data = response.model_dump()
        expected = {
            "email": "test@example.com",
            "is_suppressed": True,
            "reason": "BOUNCE",
            "last_update_time": "2024-01-15T10:30:00Z",
            "human_readable_explanation": "Email bounced"
        }
        
        assert data == expected
    
    def test_response_json_serialization(self):
        """Test response model JSON serialization"""
        response = EmailCheckResponse(
            email="test@example.com",
            is_suppressed=True,
            reason="COMPLAINT",
            last_update_time="2024-01-15T10:30:00Z",
            human_readable_explanation="Spam complaint"
        )
        
        json_str = response.model_dump_json()
        assert "test@example.com" in json_str
        assert "true" in json_str  # JSON boolean
        assert "COMPLAINT" in json_str


class TestSuppressionInfo:
    """Test cases for SuppressionInfo model"""
    
    def test_valid_suppression_info(self):
        """Test valid suppression info creation"""
        info = SuppressionInfo(
            email_address="test@example.com",
            reason="COMPLAINT",
            last_update_time="2024-01-15T10:30:00Z"
        )
        
        assert info.email_address == "test@example.com"
        assert info.reason == "COMPLAINT"
        assert info.last_update_time == "2024-01-15T10:30:00Z"
    
    def test_suppression_info_all_reasons(self):
        """Test suppression info with all valid reasons"""
        reasons = ["COMPLAINT", "BOUNCE", "UNSUBSCRIBE", "REPUTATION"]
        
        for reason in reasons:
            info = SuppressionInfo(
                email_address=f"test.{reason.lower()}@example.com",
                reason=reason,
                last_update_time="2024-01-15T10:30:00Z"
            )
            assert info.reason == reason
    
    def test_suppression_info_missing_fields(self):
        """Test suppression info with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            SuppressionInfo()
        
        error_str = str(exc_info.value)
        assert "Field required" in error_str
    
    def test_suppression_info_empty_email(self):
        """Test suppression info with empty email"""
        with pytest.raises(ValidationError) as exc_info:
            SuppressionInfo(
                email_address="",
                reason="COMPLAINT",
                last_update_time="2024-01-15T10:30:00Z"
            )
        
        # Empty string should be invalid for email_address
        assert "ensure this value has at least 1 character" in str(exc_info.value) or "String should have at least 1 character" in str(exc_info.value)
    
    def test_suppression_info_empty_reason(self):
        """Test suppression info with empty reason"""
        with pytest.raises(ValidationError) as exc_info:
            SuppressionInfo(
                email_address="test@example.com",
                reason="",
                last_update_time="2024-01-15T10:30:00Z"
            )
        
        # Empty string should be invalid for reason
        assert "ensure this value has at least 1 character" in str(exc_info.value) or "String should have at least 1 character" in str(exc_info.value)
    
    def test_suppression_info_serialization(self):
        """Test suppression info serialization"""
        info = SuppressionInfo(
            email_address="test@example.com",
            reason="BOUNCE",
            last_update_time="2024-01-15T10:30:00Z"
        )
        
        data = info.model_dump()
        expected = {
            "email_address": "test@example.com",
            "reason": "BOUNCE",
            "last_update_time": "2024-01-15T10:30:00Z"
        }
        
        assert data == expected


class TestModelIntegration:
    """Integration tests for model interactions"""
    
    def test_request_to_response_flow(self):
        """Test the flow from request to response models"""
        # Create a request
        request = EmailCheckRequest(email="test@example.com")
        
        # Create a response based on the request
        response = EmailCheckResponse(
            email=request.email,
            is_suppressed=True,
            reason="COMPLAINT",
            last_update_time="2024-01-15T10:30:00Z",
            human_readable_explanation="Email suppressed due to complaints"
        )
        
        assert response.email == request.email
        assert response.is_suppressed is True
    
    def test_suppression_info_to_response_conversion(self):
        """Test converting SuppressionInfo to EmailCheckResponse"""
        suppression_info = SuppressionInfo(
            email_address="test@example.com",
            reason="BOUNCE",
            last_update_time="2024-01-15T10:30:00Z"
        )
        
        response = EmailCheckResponse(
            email=suppression_info.email_address,
            is_suppressed=True,
            reason=suppression_info.reason,
            last_update_time=suppression_info.last_update_time,
            human_readable_explanation="Generated explanation"
        )
        
        assert response.email == suppression_info.email_address
        assert response.reason == suppression_info.reason
        assert response.last_update_time == suppression_info.last_update_time
        assert response.is_suppressed is True
