import os
from dotenv import load_dotenv

from logger import Logger
from submission_tracker import SubmissionTracker
from leetcode_api import LeetCodeAPI
from github_sync import GitHubSync

def main():
    load_dotenv()

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
    CSRF_TOKEN = os.getenv("LEETCODE_CSRF")
    LEETCODE_USERNAME = os.getenv("LEETCODE_USERNAME")
    REPO_NAME = os.getenv("REPO_NAME", "username/LeetCode")

    logger = Logger()
    tracker = SubmissionTracker()

    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN is not defined in the environment variables.")
        return

    if not LEETCODE_SESSION or not CSRF_TOKEN or not LEETCODE_USERNAME:
        logger.error("LEETCODE_SESSION, LEETCODE_CSRF, or LEETCODE_USERNAME is not defined in the environment variables.")
        return

    try:
        github_sync = GitHubSync(GITHUB_TOKEN, REPO_NAME, logger)
        leetcode = LeetCodeAPI(LEETCODE_SESSION, CSRF_TOKEN, logger)
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        return

    github_sync.sync_submissions(leetcode, tracker, LEETCODE_USERNAME, limit=20)

if __name__ == "__main__":
    main()