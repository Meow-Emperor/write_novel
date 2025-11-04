from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

# Create a rate limiter instance
limiter = Limiter(key_func=get_remote_address)
