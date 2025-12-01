from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re

def validate_https_hostname(value):
    parsed = urlparse(value)

    if parsed.scheme != "https":
        raise ValidationError("URL must use HTTPS.")

    hostname = parsed.hostname
    if not hostname:
        raise ValidationError("URL must contain a valid hostname.")

    if hostname.lower() in ("localhost", "127.0.0.1"):
        raise ValidationError("Localhost URLs are not allowed.")

    ipv4_regex = r"^\d{1,3}(\.\d{1,3}){3}$"
    ipv6_regex = r"^\[?[0-9a-fA-F:]+\]?$"

    if re.match(ipv4_regex, hostname) or re.match(ipv6_regex, hostname):
        raise ValidationError("IP addresses are not allowed, only hostnames.")

    fqdn_regex = r"^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    if not re.match(fqdn_regex, hostname):
        raise ValidationError("Invalid hostname format.")

