"""rate_limit -- "too many attempts, try again later".

    limiter.py    the shared limiter; routes add @limiter.limit("5/minute")
    keys.py       per_user: count a signed-in user's requests, not their IP's
    responses.py  the JSON 429 reply (with Retry-After) + an audit event
"""
