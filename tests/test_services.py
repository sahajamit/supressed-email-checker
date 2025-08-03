import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from services import SuppressionService, OllamaService
from models import SuppressionInfo
from config import config


class TestSuppressionService:
    """Test cases for SuppressionService"""
    
    def test_load_suppressed_emails_success(self, suppression_service_with_test_data):
        """Test successful loading of suppressed emails"""
        service = suppression_service_with_test_data
        assert len(service.suppressed_emails_data) == 4
        
        # Check first email
        first_email = service.suppressed_emails_data[0]
        assert first_email.email_address == "test.complaint@example.com"
        assert first_email.reason == "COMPLAINT"
        assert first_email.last_update_time == "2024-01-15T10:30:00Z"
    
    def test_load_suppressed_emails_file_not_found(self):
        """Test handling of missing JSON file"""
        with patch.object(config, 'SUPPRESSED_EMAILS_JSON_PATH', 'nonexistent.json'):
            service = SuppressionService()
            assert service.suppressed_emails_data == []
    
    def test_load_suppressed_emails_invalid_json(self):
        """Test handling of invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            with patch.object(config, 'SUPPRESSED_EMAILS_JSON_PATH', temp_file):
                service = SuppressionService()
                assert service.suppressed_emails_data == []
        finally:
            os.unlink(temp_file)
    
    def test_check_email_suppression_found(self, suppression_service_with_test_data):
        """Test finding a suppressed email"""
        service = suppression_service_with_test_data
        result = service.check_email_suppression("test.complaint@example.com")
        
        assert result is not None
        assert result.email_address == "test.complaint@example.com"
        assert result.reason == "COMPLAINT"
        assert result.last_update_time == "2024-01-15T10:30:00Z"
    
    def test_check_email_suppression_not_found(self, suppression_service_with_test_data):
        """Test checking a non-suppressed email"""
        service = suppression_service_with_test_data
        result = service.check_email_suppression("valid@example.com")
        
        assert result is None
    
    def test_check_email_suppression_case_insensitive(self, suppression_service_with_test_data):
        """Test case-insensitive email checking"""
        service = suppression_service_with_test_data
        result = service.check_email_suppression("TEST.COMPLAINT@EXAMPLE.COM")
        
        assert result is not None
        assert result.email_address == "test.complaint@example.com"
    
    def test_format_datetime_human_readable(self, suppression_service_with_test_data):
        """Test datetime formatting"""
        service = suppression_service_with_test_data
        formatted = service._format_datetime_human_readable("2024-01-15T10:30:00Z")
        
        assert "January 15, 2024" in formatted
        assert "10:30 AM UTC" in formatted
    
    def test_format_datetime_invalid(self, suppression_service_with_test_data):
        """Test handling of invalid datetime"""
        service = suppression_service_with_test_data
        invalid_datetime = "invalid-datetime"
        formatted = service._format_datetime_human_readable(invalid_datetime)
        
        assert formatted == invalid_datetime
    
    def test_get_reason_explanation_complaint(self, suppression_service_with_test_data):
        """Test reason explanation for COMPLAINT"""
        service = suppression_service_with_test_data
        explanation = service._get_reason_explanation("COMPLAINT")
        
        assert "marked emails from this sender as spam" in explanation
    
    def test_get_reason_explanation_bounce(self, suppression_service_with_test_data):
        """Test reason explanation for BOUNCE"""
        service = suppression_service_with_test_data
        explanation = service._get_reason_explanation("BOUNCE")
        
        assert "consistently bounce back" in explanation
    
    def test_get_reason_explanation_unsubscribe(self, suppression_service_with_test_data):
        """Test reason explanation for UNSUBSCRIBE"""
        service = suppression_service_with_test_data
        explanation = service._get_reason_explanation("UNSUBSCRIBE")
        
        assert "unsubscribed from receiving emails" in explanation
    
    def test_get_reason_explanation_reputation(self, suppression_service_with_test_data):
        """Test reason explanation for REPUTATION"""
        service = suppression_service_with_test_data
        explanation = service._get_reason_explanation("REPUTATION")
        
        assert "reputation has been negatively affected" in explanation
    
    def test_get_reason_explanation_unknown(self, suppression_service_with_test_data):
        """Test reason explanation for unknown reason"""
        service = suppression_service_with_test_data
        explanation = service._get_reason_explanation("UNKNOWN_REASON")
        
        assert "suppressed due to unknown_reason" in explanation


class TestOllamaService:
    """Test cases for OllamaService"""
    
    @patch('ollama.Client')
    def test_generate_human_explanation_success(self, mock_client_class):
        """Test successful AI explanation generation"""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.chat.return_value = {
            'message': {
                'content': 'The email test@example.com is suppressed due to complaints.'
            }
        }
        
        service = OllamaService()
        result = service.generate_human_explanation(
            email="test@example.com",
            reason="COMPLAINT",
            last_update_time="2024-01-15T10:30:00Z",
            formatted_time="January 15, 2024 at 10:30 AM UTC",
            reason_explanation="recipient marked emails as spam"
        )
        
        assert result == "The email test@example.com is suppressed due to complaints."
        mock_client.chat.assert_called_once()
    
    @patch('ollama.Client')
    def test_generate_human_explanation_with_thinking_tags(self, mock_client_class):
        """Test AI explanation with thinking tags that should be removed"""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.chat.return_value = {
            'message': {
                'content': '<think>Let me think about this...</think>The email is suppressed due to complaints.<thinking>More thinking</thinking>'
            }
        }
        
        service = OllamaService()
        result = service.generate_human_explanation(
            email="test@example.com",
            reason="COMPLAINT",
            last_update_time="2024-01-15T10:30:00Z",
            formatted_time="January 15, 2024 at 10:30 AM UTC",
            reason_explanation="recipient marked emails as spam"
        )
        
        assert result == "The email is suppressed due to complaints."
        assert "<think>" not in result
        assert "<thinking>" not in result
    
    @patch('ollama.Client')
    def test_generate_human_explanation_ollama_error(self, mock_client_class):
        """Test fallback when Ollama fails"""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.chat.side_effect = Exception("Ollama connection failed")
        
        service = OllamaService()
        result = service.generate_human_explanation(
            email="test@example.com",
            reason="COMPLAINT",
            last_update_time="2024-01-15T10:30:00Z",
            formatted_time="January 15, 2024 at 10:30 AM UTC",
            reason_explanation="recipient marked emails as spam"
        )
        
        # Should return fallback explanation
        assert "test@example.com is suppressed because recipient marked emails as spam" in result
        assert "January 15, 2024 at 10:30 AM UTC" in result
    
    @patch('ollama.Client')
    def test_ollama_service_initialization(self, mock_client_class):
        """Test OllamaService initialization"""
        service = OllamaService()
        
        assert service.model == config.OLLAMA_MODEL
        mock_client_class.assert_called_once_with(host=config.OLLAMA_BASE_URL)
    
    @patch('ollama.Client')
    def test_generate_human_explanation_parameters(self, mock_client_class):
        """Test that correct parameters are passed to Ollama"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.chat.return_value = {
            'message': {'content': 'Test response'}
        }
        
        service = OllamaService()
        service.generate_human_explanation(
            email="test@example.com",
            reason="BOUNCE",
            last_update_time="2024-01-15T10:30:00Z",
            formatted_time="January 15, 2024 at 10:30 AM UTC",
            reason_explanation="emails consistently bounce back"
        )
        
        # Verify chat was called with correct parameters
        call_args = mock_client.chat.call_args
        assert call_args[1]['model'] == config.OLLAMA_MODEL
        assert call_args[1]['stream'] is False
        assert call_args[1]['think'] is False
        
        # Check that the prompt contains expected information
        messages = call_args[1]['messages']
        prompt_content = messages[0]['content']
        assert "test@example.com" in prompt_content
        assert "BOUNCE" in prompt_content
        assert "January 15, 2024 at 10:30 AM UTC" in prompt_content
