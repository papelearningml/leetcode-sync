import requests

class LeetCodeAPI:
    def __init__(self, session_cookie, csrf_token, logger):
        self.session = requests.Session()
        self.base_url = "https://leetcode.com"
        self.graphql_url = f"{self.base_url}/graphql"
        self.logger = logger

        self.session.cookies.set('LEETCODE_SESSION', session_cookie, domain='.leetcode.com')
        self.session.cookies.set('csrftoken', csrf_token, domain='.leetcode.com')
        self.session.headers.update({
            'X-CSRFToken': csrf_token,
            'Referer': 'https://leetcode.com',
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        })

        if not self.test_connection():
            raise Exception("Failed to authenticate with LeetCode")
        else:
            self.logger.success("Connected to LeetCode")

    def test_connection(self):
        try:
            response = self.session.get(f"{self.base_url}/api/problems/all/")
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False

    def get_submission_list(self, username, limit=20):
        query = """
        query recentAcSubmissions($username: String!, $limit: Int!) {
            recentAcSubmissionList(username: $username, limit: $limit) {
                id
                title
                titleSlug
                timestamp
                statusDisplay
                lang
                runtime
                memory
                url
            }
        }
        """
        try:
            response = self.session.post(
                self.graphql_url,
                json={'query': query, 'variables': {'username': username, 'limit': limit}}
            )
            data = response.json()
            submissions = data.get('data', {}).get('recentAcSubmissionList', [])
            self.logger.info(f"Found {len(submissions)} submissions")
            return submissions
        except Exception as e:
            self.logger.error(f"Failed to fetch submissions: {e}")
            return []

    def get_submission_code(self, submission_id):
        query = """
        query submissionDetails($submissionId: Int!) {
            submissionDetails(submissionId: $submissionId) {
                code
                runtime
                memory
                runtimePercentile
                memoryPercentile
                timestamp
                lang {
                    name
                    verboseName
                }
            }
        }
        """
        try:
            response = self.session.post(
                self.graphql_url,
                json={'query': query, 'variables': {'submissionId': int(str(submission_id).strip())}}
            )
            data = response.json()
            details = data.get('data', {}).get('submissionDetails')
            if details and 'code' in details:
                self.logger.info("Code retrieved successfully")
                return details
            else:
                self.logger.error("No code found in submission details")
                return None
        except Exception as e:
            self.logger.error(f"Failed to fetch code: {e}")
            return None

    def get_problem_details(self, title_slug):
        query = """
        query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                content
                difficulty
                topicTags {
                    name
                }
            }
        }
        """
        try:
            response = self.session.post(
                self.graphql_url,
                json={'query': query, 'variables': {'titleSlug': title_slug}}
            )
            return response.json().get('data', {}).get('question')
        except Exception as e:
            self.logger.error(f"Failed to fetch problem details: {e}")
            return None