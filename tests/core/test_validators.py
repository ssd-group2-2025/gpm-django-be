import pytest
from django.core.exceptions import ValidationError
from core.validators import validate_https_hostname


def test_validator_accepts_valid_https_url():
    """Test che il validator accetti URL HTTPS validi"""
    try:
        validate_https_hostname('https://example.com')
        validate_https_hostname('https://sub.example.com')
        validate_https_hostname('https://example.co.uk')
    except ValidationError:
        pytest.fail("Valid HTTPS URL should not raise ValidationError")


def test_validator_rejects_http_url():
    """Test che il validator rifiuti URL HTTP"""
    with pytest.raises(ValidationError) as err:
        validate_https_hostname('http://example.com')
    assert 'URL must use HTTPS' in str(err.value)


def test_validator_rejects_localhost():
    """Test che il validator rifiuti localhost"""
    with pytest.raises(ValidationError) as err:
        validate_https_hostname('https://localhost')
    assert 'Localhost URLs are not allowed' in str(err.value)
    
    with pytest.raises(ValidationError) as err:
        validate_https_hostname('https://localhost:8000')
    assert 'Localhost URLs are not allowed' in str(err.value)


def test_validator_rejects_127001():
    """Test che il validator rifiuti 127.0.0.1"""
    with pytest.raises(ValidationError) as err:
        validate_https_hostname('https://127.0.0.1')
    assert 'Localhost URLs are not allowed' in str(err.value)


def test_validator_rejects_ipv4():
    """Test che il validator rifiuti indirizzi IPv4"""
    with pytest.raises(ValidationError) as err:
        validate_https_hostname('https://192.168.1.1')
    assert 'IP addresses are not allowed' in str(err.value)


def test_validator_rejects_ipv6():
    """Test che il validator rifiuti indirizzi IPv6"""
    with pytest.raises(ValidationError) as err:
        validate_https_hostname('https://[2001:db8::1]')
    assert 'IP addresses are not allowed' in str(err.value)


def test_validator_rejects_invalid_hostname():
    """Test che il validator rifiuti hostname non validi"""
    with pytest.raises(ValidationError) as err:
        validate_https_hostname('https://invalid_hostname')
    assert 'Invalid hostname format' in str(err.value)


def test_validator_rejects_url_without_hostname():
    """Test che il validator rifiuti URL senza hostname"""
    with pytest.raises(ValidationError) as err:
        validate_https_hostname('https://')
    assert 'URL must contain a valid hostname' in str(err.value)