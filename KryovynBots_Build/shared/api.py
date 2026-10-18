import json
import requests
from .config import API_URL, API_TOKEN

def call(action, **payload):
    try:
        body = json.dumps(payload, ensure_ascii=True).encode("ascii")
        r = requests.post(
            f"{API_URL}?action={action}",
            headers={
                "X-Auth-Token": API_TOKEN,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            data=body,
            timeout=12,
        )
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def link_confirm(code, platform, platform_id, tag=""):
    return call("link_confirm", code=code, platform=platform, platform_id=platform_id, tag=tag)

def profile(platform, platform_id):
    return call("profile", platform=platform, platform_id=platform_id)

def devices(platform, platform_id):
    return call("devices_list", platform=platform, platform_id=platform_id)

def revoke(platform, platform_id, device_id):
    return call("device_revoke", platform=platform, platform_id=platform_id, device_id=device_id)

def toggle_2fa(platform, platform_id, enabled):
    return call("toggle_2fa", platform=platform, platform_id=platform_id, enabled=enabled)

def unlink(platform, platform_id):
    return call("unlink", platform=platform, platform_id=platform_id)

def sessions_list(platform, platform_id):
    return call("sessions_list", platform=platform, platform_id=platform_id)

def approve(platform, platform_id, session_id):
    return call("session_approve", platform=platform, platform_id=platform_id, session_id=session_id)

def deny(platform, platform_id, session_id):
    return call("session_deny", platform=platform, platform_id=platform_id, session_id=session_id)

def tfa_poll():
    return call("tfa_poll")

def tfa_ack(id):
    return call("tfa_ack", id=id)
