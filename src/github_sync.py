import time
from github import Github

def extract_submission_id_from_url(url: str) -> int:
    # The expected format is something like: "/submissions/detail/123456789/"
    # We can split by '/' and the submission ID should be the third element:
    # ['', 'submissions', 'detail', '123456789', '']
    parts = url.strip('/').split('/')
    # parts should be ['submissions', 'detail', '123456789']
    return int(parts[-1])

class GitHubSync:
    def __init__(self, github_token, repo_name, logger):
        self.logger = logger
        self.github = Github(github_token)
        try:
            self.repo = self.github.get_repo(repo_name)
            self.logger.success("Connected to GitHub")
        except Exception as e:
            self.logger.error(f"Failed to connect to GitHub: {e}")
            raise

    def _get_best_submissions(self, submissions):
        best_submissions = {}
        for sub in submissions:
            title_slug = sub['titleSlug']
            if title_slug not in best_submissions:
                best_submissions[title_slug] = sub
            else:
                best_runtime = best_submissions[title_slug]['runtime']
                best_memory = best_submissions[title_slug]['memory']
                current_runtime = sub['runtime']
                current_memory = sub['memory']

                # Choose the submission with better performance:
                if (current_runtime < best_runtime) or (current_runtime == best_runtime and current_memory < best_memory):
                    best_submissions[title_slug] = sub
        return best_submissions

    def sync_submissions(self, leetcode, tracker, username, limit=20):
        updated_problems = []
        skipped_problems = []

        submissions = leetcode.get_submission_list(username, limit)
        if not submissions:
            self.logger.warning("No submissions found")
            return

        best_submissions = self._get_best_submissions(submissions)

        for title_slug, sub in best_submissions.items():
            self.logger.start_problem(sub['title'])

            # Extract the correct submission ID from the URL rather than using sub['id']
            submission_id = extract_submission_id_from_url(sub['url'])
            code_details = leetcode.get_submission_code(submission_id)
            if not code_details:
                continue

            problem_details = leetcode.get_problem_details(sub['titleSlug'])
            if not problem_details:
                continue

            if not tracker.should_sync(problem_details['questionId'], code_details['code']):
                self.logger.info(f"No changes needed for {sub['title']}")
                skipped_problems.append(sub['title'])
                continue

            folder_name = f"{problem_details['questionFrontendId']}_{sub['titleSlug']}"
            solution_content = code_details['code']
            readme_content = self.create_readme_content(problem_details, code_details, sub)

            extension = 'py' if code_details['lang']['name'].lower() == 'python3' else code_details['lang']['name'].lower()

            files_updated = False

            if self.create_or_update_file(
                f"{folder_name}/solution.{extension}",
                solution_content,
                f"Update solution for {problem_details['title']}"
            ):
                files_updated = True
                self.create_or_update_file(
                    f"{folder_name}/README.md",
                    readme_content,
                    f"Update documentation for {problem_details['title']}"
                )

            if files_updated:
                tracker.update_sync(problem_details['questionId'], submission_id, code_details['code'])
                updated_problems.append(sub['title'])
                self.logger.success("Synchronized successfully")
            else:
                skipped_problems.append(sub['title'])

            time.sleep(1)

        self.logger.summary(updated_problems, skipped_problems)

    def create_readme_content(self, problem_details, code_details, submission):
        problem_url = f"https://leetcode.com/problems/{problem_details['titleSlug']}"

        runtime = code_details.get('runtime', 'N/A')
        runtime_percentile = code_details.get('runtimePercentile', 0)
        memory_mb = (code_details.get('memory', 0) / 1000000) if code_details.get('memory') else 0
        memory_percentile = code_details.get('memoryPercentile', 0)

        performance_stats = f"""### Performance
- Runtime: {runtime} ms (Faster than {runtime_percentile:.2f}% of users)
- Memory: {memory_mb:.1f} MB (More efficient than {memory_percentile:.2f}% of users)"""

        return f"""# [{problem_details['title']}]({problem_url})
## Problem {problem_details['questionFrontendId']} - {problem_details['difficulty']}

### Description
{problem_details['content']}

### Tags
{', '.join(tag['name'] for tag in problem_details['topicTags'])}

{performance_stats}
"""

    def create_or_update_file(self, file_path, content, commit_message):
        try:
            # Try getting the existing file
            try:
                existing_file = self.repo.get_contents(file_path)
                existing_content = existing_file.decoded_content.decode('utf-8').strip()
                new_content = content.strip()

                if existing_content != new_content:
                    self.repo.update_file(file_path, commit_message, content, existing_file.sha)
                    self.logger.info(f"Updated {file_path}")
                    return True
                else:
                    self.logger.info(f"No changes needed for {file_path}")
                    return False
            except Exception as e:
                # If the file does not exist, create it
                if "404" in str(e):
                    self.repo.create_file(file_path, commit_message, content)
                    self.logger.info(f"Created {file_path}")
                    return True
                else:
                    raise
        except Exception as e:
            self.logger.error(f"Failed to manage file {file_path}: {e}")
            return False