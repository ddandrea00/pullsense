import requests
import json
import time

BASE_URL = "http://localhost:8000"

def send_webhook(action, pr_number, title, author="testuser"):
    """Send a test webhook to our API"""
    payload = {
        "action": action,
        "pull_request": {
            "number": pr_number,
            "title": title,
            "user": {"login": author},
            "body": f"Description for PR #{pr_number}",
            "created_at": "2024-01-15T10:30:00Z",
            "head": {"ref": "feature/test"},
            "base": {"ref": "main"}
        },
        "repository": {
            "full_name": "testorg/testrepo",
            "name": "testrepo",
            "owner": {"login": "testorg"}
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/webhook/github",
        json=payload,
        headers={
            "X-GitHub-Event": "pull_request",
            "Content-Type": "application/json"
        }
    )
    
    print(f"✅ Sent {action} event for PR #{pr_number}: {response.status_code}")
    return response

# Simulate a PR lifecycle
print("🚀 Simulating PR lifecycle...\n")

# 1. Developer opens a PR
send_webhook("opened", 201, "Add user authentication feature", "alice")
time.sleep(1)

# 2. Another developer opens a PR
send_webhook("opened", 202, "Fix memory leak in parser", "bob")
time.sleep(1)

# 3. First PR gets updated
send_webhook("synchronize", 201, "Add user authentication feature", "alice")
time.sleep(1)

# 4. Second PR is closed
send_webhook("closed", 202, "Fix memory leak in parser", "bob")

# Check what we stored
print("\n📊 Checking stored PRs...")
response = requests.get(f"{BASE_URL}/pull-requests")
data = response.json()

print(f"\nTotal PRs in database: {data['count']}")
for pr in data['pull_requests']:
    print(f"  - PR #{pr['number']}: {pr['title']} ({pr['action']})")