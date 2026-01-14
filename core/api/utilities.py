import requests
from workmania.settings import *
from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
import uuid
import random
import string
import ipaddress
from datetime import datetime


def get_ip_location(ip: str):
    """
    Best-effort GeoIP lookup.
    Returns a JSON-serializable dict or None.
    """
    if not ip:
        return None

    ip = str(ip).strip()
    try:
        ip_obj = ipaddress.ip_address(ip)
        # Skip internal/non-routable IPs
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_reserved
            or ip_obj.is_multicast
            or ip_obj.is_link_local
        ):
            return None
    except Exception:
        # Not a valid IP literal (could be hostname). Don't guess here.
        return None

    # Use a free HTTPS endpoint (rate-limited but fine for light usage).
    # Docs: https://ipapi.co/api/#complete-location
    url = f"https://ipapi.co/{ip}/json/"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code != 200:
            return None
        payload = resp.json()
    except Exception:
        return None

    # ipapi returns {"error": true, "reason": "..."} on failure
    if isinstance(payload, dict) and payload.get("error"):
        return None

    if not isinstance(payload, dict):
        return None

    payload.pop("readme", None)

    # Normalize important fields (ipapi.co keys)
    country = payload.get("country_name")
    country_code = payload.get("country_code")
    state = payload.get("region")
    state_code = payload.get("region_code")
    city = payload.get("city")
    postal = payload.get("postal")
    timezone = payload.get("timezone")
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    org = payload.get("org")
    asn = payload.get("asn")

    return {
        "ip": ip,
        "source": "ipapi.co",
        "country": country,
        "country_code": country_code,
        "state": state,
        "state_code": state_code,
        "city": city,
        "postal": postal,
        "timezone": timezone,
        "lat": latitude,
        "lon": longitude,
    }

@shared_task
def start_scraping_by_platform(platform_id):
    print(f"started background process")


def generate_random_password(length=8, is_digits_only=False):
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = '!@#$%^&*'
    
    if is_digits_only:
        return ''.join(random.choice(digits) for _ in range(length))
    
    # Ensure at least one character from each set
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special_chars)
    ]
    
    # Fill the rest with random characters from all sets
    all_chars = lowercase + uppercase + digits + special_chars
    password.extend(random.choice(all_chars) for _ in range(length - 4))
    
    # Shuffle the password
    random.shuffle(password)
    return ''.join(password)
