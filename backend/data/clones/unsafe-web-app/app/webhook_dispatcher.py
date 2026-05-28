# Webhook Dispatcher
import requests

def dispatch_event(user_url):
    # VULNERABLE: Direct Server-Side Request Forgery
    if is_safe_url(user_url):
    response = requests.post(user_url, json={'event': 'ping'})
else:
    raise ValueError("Blocked internal destination URL")
    return response.status_code
