"""Send Gmail compose via CDP - opens pre-filled compose window."""
import sys, os, urllib.parse, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from cdp_client import CDPClient, find_cdp_port

to_email = "contact.stickitup@gmail.com,wecare@stickitup.xyz"
subject = "Quick heads up on stickitup.xyz - found a few checkout & cart bugs dropping orders"

with open(os.path.join(os.path.dirname(__file__), "..", "..", "..", "antigravity", "brain",
          "c84b9177-a701-4dd4-8e6b-9175831b4120", "scratch", "email_body.txt"), "r") as f:
    body = f.read()

params = {
    "view": "cm",
    "fs": "1",
    "to": to_email,
    "su": subject,
    "body": body,
}
gmail_url = "https://mail.google.com/mail/?" + urllib.parse.urlencode(params)

port = find_cdp_port()
if not port:
    print("ERROR: CDP not available")
    sys.exit(1)

print(f"CDP available on port {port}")
cdp = CDPClient(port=port)

# Open Gmail compose in a new tab
result = cdp.new_tab(gmail_url)
print(f"Gmail compose tab opened!")
print(f"To: {to_email}")
print(f"Subject: {subject}")
print("Email is ready to review and send in your Chrome browser.")

