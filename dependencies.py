import os
from fastapi import Request


def get_client_ip(request: Request) -> str:
    if os.getenv('GAE_ENV', '').startswith('standard'):
        forwarded_for = request.headers.get('X-Forwarded-For', '')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        else:
            return request.client.host if request.client else None
    else:
        return request.client.host if request.client else None