import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_analyzer import analyzer

test_pr = {
    "title": "Add user authentication",
    "body": "This PR adds JWT authentication to our API endpoints",
    "author": "testuser"
}

result = analyzer.analyze_pr(test_pr)
print("Analysis Result:")
print("-" * 50)
print(result)