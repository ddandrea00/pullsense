import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_complete_flow():
    """Test creating a PR and getting AI analysis"""
    
    print("🚀 Testing complete PullSense flow...\n")
    
    # 1. Send a PR webhook
    pr_payload = {
        "action": "opened",
        "pull_request": {
            "number": 1001,
            "title": "Add Redis caching to improve API performance",
            "body": """This PR implements Redis caching for our API endpoints.
            
            Changes:
            - Add Redis connection manager
            - Implement cache decorators
            - Add cache invalidation logic
            - Add metrics for cache hit/miss rates
            
            This should improve response times by 50%.""",
            "user": {"login": "alice"},
        },
        "repository": {
            "full_name": "pullsense/api",
            "name": "api"
        }
    }
    
    print("1️⃣ Sending PR webhook...")
    response = requests.post(
        f"{BASE_URL}/webhook/github",
        json=pr_payload,
        headers={"X-GitHub-Event": "pull_request"}
    )
    print(f"   Response: {response.json()}")
    
    # 2. Check dashboard
    print("\n2️⃣ Checking dashboard...")
    response = requests.get(f"{BASE_URL}/dashboard")
    dashboard = response.json()
    print(f"   Total PRs: {dashboard['total_prs']}")
    print(f"   Analyzed: {dashboard['analyzed']}")
    
    # Get the PR we just created
    latest_pr = dashboard["pull_requests"][0]
    pr_id = latest_pr["pr_id"]
    print(f"   Latest PR ID: {pr_id}")
    
    # 3. Wait for analysis
    print("\n3️⃣ Waiting for AI analysis to complete...")
    for i in range(10):  # Wait up to 10 seconds
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/pull-requests/{pr_id}/analysis")
        result = response.json()
        
        if result.get("status") != "pending":
            print("   ✅ Analysis complete!")
            break
        print(f"   ... waiting {i+1}s")
    
    # 4. Display analysis
    print("\n4️⃣ Analysis Result:")
    print("-" * 50)
    if "analysis" in result:
        print(f"Status: {result['analysis']['status']}")
        print(f"Model: {result['analysis']['model']}")
        print(f"Time taken: {result['analysis'].get('analysis_time', 'N/A')}s")
        print(f"\nAnalysis Text:")
        print(result['analysis']['text'])
    else:
        print("No analysis found!")
    
    # 5. Check stats
    print("\n5️⃣ System Stats:")
    stats = requests.get(f"{BASE_URL}/stats").json()
    print(f"   Total PRs: {stats['total_prs']}")
    print(f"   Total Reviews: {stats['total_reviews']}")
    print(f"   AI Enabled: {stats['ai_enabled']}")

if __name__ == "__main__":
    test_complete_flow()