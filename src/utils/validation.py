"""
Data validation module with comprehensive input validation and type checking.

Provides:
- Email validation
- Campaign data validation
- Signup validation
- Activation validation
- Error reporting
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


class ValidationError(ValueError):
    """Custom exception for validation errors."""
    pass


class EmailValidator:
    """Email validation utilities."""
    
    # RFC 5322 simplified email regex
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    MAX_LENGTH = 255
    
    @classmethod
    def validate(cls, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, raises ValidationError otherwise
            
        Raises:
            ValidationError: If email is invalid
        """
        if not isinstance(email, str):
            raise ValidationError(f"Email must be string, got {type(email)}")
        
        email = email.strip()
        
        if not email:
            raise ValidationError("Email cannot be empty")
        
        if len(email) > cls.MAX_LENGTH:
            raise ValidationError(f"Email exceeds max length of {cls.MAX_LENGTH}")
        
        if not cls.EMAIL_PATTERN.match(email):
            raise ValidationError(f"Invalid email format: {email}")
        
        return True
    
    @classmethod
    def sanitize(cls, email: str) -> str:
        """Sanitize and normalize email."""
        return email.strip().lower()


class CampaignDataValidator:
    """Validation for campaign metrics data."""
    
    VALID_PLATFORMS = {
        "google_ads", "meta_ads", "linkedin_ads", "tiktok_ads", "pinterest_ads"
    }
    
    @staticmethod
    def validate_campaign_id(campaign_id: str) -> bool:
        """Validate campaign ID."""
        if not isinstance(campaign_id, str) or not campaign_id.strip():
            raise ValidationError("Campaign ID must be non-empty string")
        return True
    
    @staticmethod
    def validate_platform(platform: str) -> bool:
        """Validate ad platform."""
        if platform not in CampaignDataValidator.VALID_PLATFORMS:
            raise ValidationError(
                f"Invalid platform '{platform}'. Must be one of: "
                f"{', '.join(CampaignDataValidator.VALID_PLATFORMS)}"
            )
        return True
    
    @staticmethod
    def validate_spend(spend_usd: float) -> bool:
        """Validate spend amount."""
        try:
            spend = float(spend_usd)
            if spend < 0:
                raise ValidationError("Spend cannot be negative")
            return True
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid spend amount: {spend_usd}")
    
    @staticmethod
    def validate_metric(value: int) -> bool:
        """Validate numeric metrics (clicks, impressions)."""
        try:
            val = int(value)
            if val < 0:
                raise ValidationError("Metrics cannot be negative")
            return True
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid metric value: {value}")
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except (ValueError, TypeError):
            raise ValidationError(
                f"Invalid date format: {date_str}. Expected YYYY-MM-DD"
            )
    
    @classmethod
    def validate_campaign_metrics(cls, data: Dict[str, Any]) -> bool:
        """
        Validate complete campaign metrics record.
        
        Args:
            data: Campaign metrics dictionary
            
        Returns:
            True if valid, raises ValidationError otherwise
        """
        required_fields = {
            "campaign_id", "ad_platform", "spend_usd",
            "clicks", "impressions", "sync_date"
        }
        
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            raise ValidationError(f"Missing required fields: {missing_fields}")
        
        cls.validate_campaign_id(data["campaign_id"])
        cls.validate_platform(data["ad_platform"])
        cls.validate_spend(data["spend_usd"])
        cls.validate_metric(data["clicks"])
        cls.validate_metric(data["impressions"])
        cls.validate_date(data["sync_date"])
        
        # Ensure clicks <= impressions
        if int(data["clicks"]) > int(data["impressions"]):
            raise ValidationError("Clicks cannot exceed impressions")
        
        return True


class SignupValidator:
    """Validation for signup data."""
    
    @classmethod
    def validate_signup(cls, data: Dict[str, Any]) -> bool:
        """
        Validate signup record.
        
        Args:
            data: Signup dictionary
            
        Returns:
            True if valid, raises ValidationError otherwise
        """
        required_fields = {"email", "signup_timestamp"}
        missing_fields = required_fields - set(data.keys())
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {missing_fields}")
        
        EmailValidator.validate(data["email"])
        
        # Validate timestamp
        try:
            datetime.fromisoformat(data["signup_timestamp"].replace("Z", "+00:00"))
        except (ValueError, TypeError, AttributeError):
            raise ValidationError(
                f"Invalid signup timestamp: {data['signup_timestamp']}"
            )
        
        return True


class ActivationValidator:
    """Validation for activation data."""
    
    @classmethod
    def validate_activation(cls, data: Dict[str, Any]) -> bool:
        """
        Validate activation record.
        
        Args:
            data: Activation dictionary
            
        Returns:
            True if valid, raises ValidationError otherwise
        """
        required_fields = {
            "user_id", "email", "signup_timestamp",
            "profile_completed", "campaign_run"
        }
        missing_fields = required_fields - set(data.keys())
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {missing_fields}")
        
        # Validate email
        EmailValidator.validate(data["email"])
        
        # Validate timestamps
        try:
            signup_time = datetime.fromisoformat(
                data["signup_timestamp"].replace("Z", "+00:00")
            )
        except (ValueError, TypeError, AttributeError):
            raise ValidationError(
                f"Invalid signup timestamp: {data['signup_timestamp']}"
            )
        
        # Validate activation timestamp if present
        if data.get("activation_timestamp"):
            try:
                activation_time = datetime.fromisoformat(
                    data["activation_timestamp"].replace("Z", "+00:00")
                )
                
                # Activation must occur after signup
                if activation_time < signup_time:
                    raise ValidationError(
                        "Activation timestamp cannot be before signup timestamp"
                    )
            except (ValueError, TypeError, AttributeError):
                raise ValidationError(
                    f"Invalid activation timestamp: {data['activation_timestamp']}"
                )
        
        # Validate boolean fields
        for field in ["profile_completed", "campaign_run"]:
            if not isinstance(data[field], (bool, int)):
                raise ValidationError(f"{field} must be boolean")
        
        return True


class ValidationBatch:
    """Batch validation with error collection."""
    
    def __init__(self):
        """Initialize batch validator."""
        self.errors: List[Tuple[str, int, str]] = []
        self.valid_count: int = 0
    
    def validate_campaigns(
        self, campaigns: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Tuple[str, int, str]]]:
        """
        Validate batch of campaign records.
        
        Returns:
            Tuple of (valid_records, errors_with_line_numbers)
        """
        valid_records = []
        
        for idx, record in enumerate(campaigns, start=1):
            try:
                CampaignDataValidator.validate_campaign_metrics(record)
                valid_records.append(record)
                self.valid_count += 1
            except ValidationError as e:
                self.errors.append(("campaign_metrics", idx, str(e)))
        
        return valid_records, self.errors
    
    def validate_signups(
        self, signups: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Tuple[str, int, str]]]:
        """
        Validate batch of signup records.
        
        Returns:
            Tuple of (valid_records, errors_with_line_numbers)
        """
        valid_records = []
        
        for idx, record in enumerate(signups, start=1):
            try:
                SignupValidator.validate_signup(record)
                valid_records.append(record)
                self.valid_count += 1
            except ValidationError as e:
                self.errors.append(("signup", idx, str(e)))
        
        return valid_records, self.errors
    
    def validate_activations(
        self, activations: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Tuple[str, int, str]]]:
        """
        Validate batch of activation records.
        
        Returns:
            Tuple of (valid_records, errors_with_line_numbers)
        """
        valid_records = []
        
        for idx, record in enumerate(activations, start=1):
            try:
                ActivationValidator.validate_activation(record)
                valid_records.append(record)
                self.valid_count += 1
            except ValidationError as e:
                self.errors.append(("activation", idx, str(e)))
        
        return valid_records, self.errors
    
    def get_error_summary(self) -> str:
        """Get formatted error summary."""
        if not self.errors:
            return f"✓ All {self.valid_count} records validated successfully"
        
        summary = f"✓ Valid: {self.valid_count} | ✗ Invalid: {len(self.errors)}\n\n"
        
        for record_type, line_num, error in self.errors:
            summary += f"[{record_type}:{line_num}] {error}\n"
        
        return summary
    
    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self.errors) > 0
