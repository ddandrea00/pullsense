from services.cache_service import cache
from github import Github
from typing import Optional, Dict
import os
from config import settings


class GitHubService:
    """
    Service for interacting with GitHub API.
    Fetches real PR data, code diffs, and file contents.
    """
    
    def __init__(self):
        # Use token if available, otherwise anonymous (limited rate)
        self.github_token = os.getenv("GITHUB_TOKEN")
        if self.github_token:
            self.client = Github(self.github_token)
            print("✅ GitHub client initialized with token")
        else:
            self.client = Github()
            print("⚠️  GitHub client initialized without token (rate limited)")
    
    def get_pr_diff(self, repo_full_name: str, pr_number: int) -> Optional[Dict]:
        """
        Fetch pull request details and diff from GitHub.
        
        Returns:
            Dict with PR details and file changes
        """
          # Check cache first
        cache_key = f"github_diff:{repo_full_name}:{pr_number}"
        cached_data = cache.get(cache_key)
        if cached_data:
            print(f"📦 Using cached GitHub data for {repo_full_name} PR #{pr_number}")
            return cached_data
        
        try:
            # Get repository
            repo = self.client.get_repo(repo_full_name)
            
            # Get pull request
            pr = repo.get_pull(pr_number)
            
            # Get files changed
            files = pr.get_files()
            
            # Build diff data
            diff_data = {
                "title": pr.title,
                "body": pr.body,
                "state": pr.state,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "changed_files": pr.changed_files,
                "mergeable": pr.mergeable,
                "files": []
            }
            
            # Get individual file diffs (limit to prevent huge responses)
            for file in files[:10]:  # Max 10 files
                diff_data["files"].append({
                    "filename": file.filename,
                    "status": file.status,  # added, removed, modified
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "patch": file.patch if file.patch else "Binary file or too large"
                })
                
            if diff_data:
                cache.set(cache_key, diff_data, expire=3600)  # Cache for 1 hour
                print(f"💾 Cached GitHub data for {repo_full_name} PR #{pr_number}")
            
            
                return diff_data

            
        except Exception as e:
            print(f"❌ GitHub API error: {e}")
            return None
    
    def get_rate_limit(self) -> Dict:
        """Check GitHub API rate limit status."""
        try:
            rate_limit = self.client.get_rate_limit()
            return {
                "limit": rate_limit.core.limit,
                "remaining": rate_limit.core.remaining,
                "reset": rate_limit.core.reset.isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

# Singleton instance
github_service = GitHubService()