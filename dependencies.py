from fastapi import Request


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        client_ip = forwarded.split(',')[-1].strip()
    else:
        client_ip = request.client.host

    return client_ip