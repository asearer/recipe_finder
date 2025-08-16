import pytest
from datetime import timedelta
from jose import jwt
from backend.auth import (
    verify_password, get_password_hash, create_access_token, 
    decode_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
)


class TestPasswordHashing:
    """Test cases for password hashing functionality."""
    
    def test_password_hashing_and_verification(self):
        """Test that password hashing and verification work correctly."""
        plain_password = "testpassword123"
        hashed_password = get_password_hash(plain_password)
        
        # Verify the password matches
        assert verify_password(plain_password, hashed_password) is True
        
        # Verify wrong password doesn't match
        assert verify_password("wrongpassword", hashed_password) is False
    
    def test_password_hash_is_different(self):
        """Test that hashed passwords are different from plain text."""
        plain_password = "testpassword123"
        hashed_password = get_password_hash(plain_password)
        
        assert hashed_password != plain_password
        assert len(hashed_password) > len(plain_password)
    
    def test_same_password_different_hash(self):
        """Test that the same password produces different hashes."""
        plain_password = "testpassword123"
        hash1 = get_password_hash(plain_password)
        hash2 = get_password_hash(plain_password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
    
    def test_empty_password(self):
        """Test handling of empty password."""
        empty_password = ""
        hashed_password = get_password_hash(empty_password)
        
        assert verify_password(empty_password, hashed_password) is True
        assert verify_password("wrong", hashed_password) is False
    
    def test_special_characters_password(self):
        """Test password with special characters."""
        special_password = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        hashed_password = get_password_hash(special_password)
        
        assert verify_password(special_password, hashed_password) is True
        assert verify_password("wrong", hashed_password) is False


class TestAccessTokenCreation:
    """Test cases for JWT access token creation."""
    
    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify the token
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
    
    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry."""
        data = {"sub": "testuser"}
        custom_expiry = timedelta(hours=2)
        token = create_access_token(data, expires_delta=custom_expiry)
        
        assert token is not None
        
        # Decode and verify the token
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
    
    def test_create_access_token_with_additional_data(self):
        """Test creating access token with additional data."""
        data = {
            "sub": "testuser",
            "role": "admin",
            "permissions": ["read", "write"]
        }
        token = create_access_token(data)
        
        assert token is not None
        
        # Decode and verify the token
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]
    
    def test_create_access_token_empty_data(self):
        """Test creating access token with empty data."""
        data = {}
        token = create_access_token(data)
        
        assert token is not None
        
        # Decode and verify the token
        payload = decode_access_token(token)
        assert payload is not None
        assert "exp" in payload
    
    def test_create_access_token_none_expiry(self):
        """Test creating access token with None expiry (should use default)."""
        data = {"sub": "testuser"}
        token = create_access_token(data, expires_delta=None)
        
        assert token is not None
        
        # Decode and verify the token
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"


class TestAccessTokenDecoding:
    """Test cases for JWT access token decoding."""
    
    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
    
    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"
        payload = decode_access_token(invalid_token)
        
        assert payload is None
    
    def test_decode_empty_token(self):
        """Test decoding an empty token."""
        empty_token = ""
        payload = decode_access_token(empty_token)
        
        assert payload is None
    
    def test_decode_none_token(self):
        """Test decoding a None token."""
        # This should handle None gracefully
        payload = decode_access_token(None)
        
        assert payload is None
    
    def test_decode_malformed_token(self):
        """Test decoding a malformed token."""
        malformed_token = "not.a.valid.jwt.token"
        payload = decode_access_token(malformed_token)
        
        assert payload is None
    
    def test_decode_token_with_wrong_secret(self):
        """Test that tokens created with wrong secret cannot be decoded."""
        # Create token with correct secret
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # Try to decode with wrong secret
        wrong_secret = "WRONG_SECRET_KEY"
        try:
            payload = jwt.decode(token, wrong_secret, algorithms=[ALGORITHM])
            # If we get here, the test should fail
            assert False, "Token should not be decodable with wrong secret"
        except jwt.JWTError:
            # This is expected
            pass


class TestTokenExpiry:
    """Test cases for token expiry functionality."""
    
    def test_token_has_expiry_field(self):
        """Test that created tokens have an expiry field."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        payload = decode_access_token(token)
        assert payload is not None
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
    
    def test_token_expiry_is_future(self):
        """Test that token expiry is in the future."""
        import time
        
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        payload = decode_access_token(token)
        assert payload is not None
        
        current_time = int(time.time())
        assert payload["exp"] > current_time
    
    def test_custom_expiry_time(self):
        """Test that custom expiry time is respected."""
        data = {"sub": "testuser"}
        custom_expiry = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=custom_expiry)
        
        payload = decode_access_token(token)
        assert payload is not None
        
        # The expiry should be approximately 30 minutes from now
        import time
        current_time = int(time.time())
        expected_expiry = current_time + (30 * 60)
        
        # Allow for some time difference (within 5 seconds)
        assert abs(payload["exp"] - expected_expiry) < 5


class TestConstants:
    """Test cases for authentication constants."""
    
    def test_secret_key_exists(self):
        """Test that SECRET_KEY is defined."""
        assert SECRET_KEY is not None
        assert isinstance(SECRET_KEY, str)
        assert len(SECRET_KEY) > 0
    
    def test_algorithm_exists(self):
        """Test that ALGORITHM is defined."""
        assert ALGORITHM is not None
        assert ALGORITHM == "HS256"
    
    def test_access_token_expire_minutes_exists(self):
        """Test that ACCESS_TOKEN_EXPIRE_MINUTES is defined."""
        assert ACCESS_TOKEN_EXPIRE_MINUTES is not None
        assert isinstance(ACCESS_TOKEN_EXPIRE_MINUTES, int)
        assert ACCESS_TOKEN_EXPIRE_MINUTES > 0
    
    def test_default_expiry_is_reasonable(self):
        """Test that default expiry time is reasonable (7 days)."""
        expected_minutes = 60 * 24 * 7  # 7 days
        assert ACCESS_TOKEN_EXPIRE_MINUTES == expected_minutes


class TestEdgeCases:
    """Test cases for edge cases and error conditions."""
    
    def test_very_long_username(self):
        """Test token creation with very long username."""
        long_username = "a" * 1000
        data = {"sub": long_username}
        token = create_access_token(data)
        
        assert token is not None
        
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == long_username
    
    def test_unicode_characters(self):
        """Test token creation with unicode characters."""
        unicode_username = "testuser_ñáéíóú_测试_тест"
        data = {"sub": unicode_username}
        token = create_access_token(data)
        
        assert token is not None
        
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == unicode_username
    
    def test_numeric_username(self):
        """Test token creation with numeric username."""
        numeric_username = "12345"
        data = {"sub": numeric_username}
        token = create_access_token(data)
        
        assert token is not None
        
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == numeric_username
    
    def test_special_characters_in_data(self):
        """Test token creation with special characters in data."""
        special_data = {
            "sub": "testuser",
            "email": "test@example.com",
            "phone": "+1-555-123-4567",
            "address": "123 Main St, Apt #4B, City, ST 12345"
        }
        token = create_access_token(special_data)
        
        assert token is not None
        
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == special_data["sub"]
        assert payload["email"] == special_data["email"]
        assert payload["phone"] == special_data["phone"]
        assert payload["address"] == special_data["address"]
