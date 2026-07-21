"""
Unit tests for validation module.
"""

import pytest
from src.utils.validation import (
    ValidationError,
    EmailValidator,
    CampaignDataValidator,
    SignupValidator,
    ActivationValidator,
    ValidationBatch,
)


class TestEmailValidator:
    """Test email validation."""
    
    def test_valid_emails(self):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@example.co.uk",
            "user+tag@example.com",
            "user_name@example.com",
        ]
        
        for email in valid_emails:
            assert EmailValidator.validate(email)
    
    def test_invalid_emails(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "invalid",
            "invalid@",
            "@invalid.com",
            "invalid @example.com",
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                EmailValidator.validate(email)
    
    def test_email_sanitization(self):
        """Test email sanitization."""
        email = "  TEST@EXAMPLE.COM  "
        sanitized = EmailValidator.sanitize(email)
        assert sanitized == "test@example.com"
    
    def test_email_max_length(self):
        """Test email max length validation."""
        long_email = "a" * 256 + "@example.com"
        with pytest.raises(ValidationError):
            EmailValidator.validate(long_email)


class TestCampaignDataValidator:
    """Test campaign data validation."""
    
    def test_valid_campaign_metrics(self):
        """Test valid campaign metrics."""
        data = {
            "campaign_id": "c_google_brand",
            "ad_platform": "google_ads",
            "spend_usd": 100.0,
            "clicks": 50,
            "impressions": 1000,
            "sync_date": "2024-01-15",
        }
        
        assert CampaignDataValidator.validate_campaign_metrics(data)
    
    def test_invalid_platform(self):
        """Test invalid ad platform."""
        with pytest.raises(ValidationError):
            CampaignDataValidator.validate_platform("invalid_platform")
    
    def test_negative_spend(self):
        """Test negative spend validation."""
        with pytest.raises(ValidationError):
            CampaignDataValidator.validate_spend(-100)
    
    def test_clicks_exceed_impressions(self):
        """Test clicks cannot exceed impressions."""
        data = {
            "campaign_id": "c_google_brand",
            "ad_platform": "google_ads",
            "spend_usd": 100.0,
            "clicks": 2000,  # Exceeds impressions
            "impressions": 1000,
            "sync_date": "2024-01-15",
        }
        
        with pytest.raises(ValidationError):
            CampaignDataValidator.validate_campaign_metrics(data)
    
    def test_invalid_date_format(self):
        """Test invalid date format."""
        with pytest.raises(ValidationError):
            CampaignDataValidator.validate_date("2024/01/15")


class TestSignupValidator:
    """Test signup validation."""
    
    def test_valid_signup(self):
        """Test valid signup record."""
        data = {
            "email": "user@example.com",
            "utm_campaign": "c_google_brand",
            "signup_timestamp": "2024-01-15T10:30:00",
        }
        
        assert SignupValidator.validate_signup(data)
    
    def test_missing_email(self):
        """Test missing email field."""
        data = {
            "utm_campaign": "c_google_brand",
            "signup_timestamp": "2024-01-15T10:30:00",
        }
        
        with pytest.raises(ValidationError):
            SignupValidator.validate_signup(data)
    
    def test_invalid_email_in_signup(self):
        """Test invalid email in signup."""
        data = {
            "email": "invalid-email",
            "utm_campaign": "c_google_brand",
            "signup_timestamp": "2024-01-15T10:30:00",
        }
        
        with pytest.raises(ValidationError):
            SignupValidator.validate_signup(data)


class TestActivationValidator:
    """Test activation validation."""
    
    def test_valid_activation(self):
        """Test valid activation record."""
        data = {
            "user_id": "usr_001",
            "email": "user@example.com",
            "signup_timestamp": "2024-01-15T10:30:00",
            "activation_timestamp": "2024-01-16T10:30:00",
            "profile_completed": True,
            "campaign_run": True,
        }
        
        assert ActivationValidator.validate_activation(data)
    
    def test_activation_before_signup(self):
        """Test activation cannot occur before signup."""
        data = {
            "user_id": "usr_001",
            "email": "user@example.com",
            "signup_timestamp": "2024-01-16T10:30:00",
            "activation_timestamp": "2024-01-15T10:30:00",  # Before signup
            "profile_completed": True,
            "campaign_run": True,
        }
        
        with pytest.raises(ValidationError):
            ActivationValidator.validate_activation(data)


class TestValidationBatch:
    """Test batch validation."""
    
    def test_batch_campaigns_validation(self):
        """Test validating batch of campaigns."""
        campaigns = [
            {
                "campaign_id": "c_google_brand",
                "ad_platform": "google_ads",
                "spend_usd": 100.0,
                "clicks": 50,
                "impressions": 1000,
                "sync_date": "2024-01-15",
            },
            {
                "campaign_id": "c_meta_retarget",
                "ad_platform": "meta_ads",
                "spend_usd": 200.0,
                "clicks": 100,
                "impressions": 2000,
                "sync_date": "2024-01-15",
            },
        ]
        
        validator = ValidationBatch()
        valid, errors = validator.validate_campaigns(campaigns)
        
        assert len(valid) == 2
        assert len(errors) == 0
    
    def test_batch_validation_with_errors(self):
        """Test batch validation collects errors."""
        campaigns = [
            {
                "campaign_id": "c_google_brand",
                "ad_platform": "google_ads",
                "spend_usd": 100.0,
                "clicks": 50,
                "impressions": 1000,
                "sync_date": "2024-01-15",
            },
            {
                "campaign_id": "c_invalid",
                "ad_platform": "invalid_platform",  # Invalid
                "spend_usd": 200.0,
                "clicks": 100,
                "impressions": 2000,
                "sync_date": "2024-01-15",
            },
        ]
        
        validator = ValidationBatch()
        valid, errors = validator.validate_campaigns(campaigns)
        
        assert len(valid) == 1
        assert len(errors) == 1
        assert validator.has_errors()
