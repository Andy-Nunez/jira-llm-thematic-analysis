"""
LLM-based analyzer for extracting delay themes from JIRA comments.
Uses OpenAI GPT models to identify root causes and sentiment.
"""

import os
import time
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class DelayThemeAnalyzer:
    """Analyzes JIRA comments to extract delay themes using GPT."""

    def __init__(self):
        """Initialize the OpenAI client with API key from environment."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. "
                "Please set it in your .env file. "
                "Copy .env.example to .env and add your API key."
            )

        # Initialize client without deprecated parameters
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo')
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))

        # Rate limiting
        self.requests_per_minute = int(os.getenv('REQUESTS_PER_MINUTE', '20'))
        self.request_interval = 60.0 / self.requests_per_minute
        self.last_request_time = 0

    def _rate_limit(self):
        """Implement simple rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_interval:
            time.sleep(self.request_interval - time_since_last)

        self.last_request_time = time.time()

    def extract_delay_theme(
        self,
        comment_text: str,
        issue_key: str = "Unknown"
    ) -> Dict[str, str]:
        """
        Extract delay theme and sentiment from a JIRA comment.

        Args:
            comment_text: The JIRA comment text to analyze
            issue_key: JIRA issue identifier for reference

        Returns:
            Dictionary with theme, sentiment, and reasoning
        """
        self._rate_limit()

        prompt = f"""You are analyzing JIRA issue comments to identify why issues were delayed from October to November.

Analyze this comment and extract:
1. The PRIMARY delay theme (root cause category)
2. Sentiment (positive, neutral, negative)
3. Brief reasoning

COMMENT:
{comment_text}

Categorize the delay into ONE of these actionable management themes:
- Technical Debt: Legacy code, outdated dependencies, refactoring needs
- Resource Constraints: Insufficient staffing, competing priorities
- Dependencies: Blocked by other teams, external vendors, infrastructure
- Requirements Issues: Unclear specs, changing requirements, scope creep
- Testing/QA: Test failures, insufficient test coverage, QA bottlenecks
- Environment Issues: Dev/staging environment problems, deployment issues
- Communication Gaps: Misalignment, lack of updates, unclear ownership
- Complexity: Underestimated effort, technical complexity
- Process Issues: Workflow inefficiencies, approval delays
- External Factors: Customer delays, vendor delays, third-party issues

Respond in this exact format:
THEME: [one of the above categories]
SENTIMENT: [positive/neutral/negative]
REASONING: [one sentence explanation]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert project manager analyzing delay root causes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            result_text = response.choices[0].message.content.strip()

            # Parse the response
            theme = "Unknown"
            sentiment = "neutral"
            reasoning = ""

            for line in result_text.split('\n'):
                line = line.strip()
                if line.startswith('THEME:'):
                    theme = line.replace('THEME:', '').strip()
                elif line.startswith('SENTIMENT:'):
                    sentiment = line.replace('SENTIMENT:', '').strip().lower()
                elif line.startswith('REASONING:'):
                    reasoning = line.replace('REASONING:', '').strip()

            return {
                'issue_key': issue_key,
                'theme': theme,
                'sentiment': sentiment,
                'reasoning': reasoning,
                'raw_response': result_text
            }

        except Exception as e:
            print(f"Error analyzing issue {issue_key}: {str(e)}")
            return {
                'issue_key': issue_key,
                'theme': 'Error',
                'sentiment': 'neutral',
                'reasoning': f'API Error: {str(e)}',
                'raw_response': ''
            }

    def batch_analyze(
        self,
        comments: list,
        issue_keys: Optional[list] = None
    ) -> list:
        """
        Analyze multiple comments in batch.

        Args:
            comments: List of comment texts
            issue_keys: Optional list of issue keys (must match comments length)

        Returns:
            List of theme analysis results
        """
        if issue_keys is None:
            issue_keys = [f"Issue_{i}" for i in range(len(comments))]

        if len(comments) != len(issue_keys):
            raise ValueError("Comments and issue_keys must have same length")

        results = []
        for comment, key in zip(comments, issue_keys):
            result = self.extract_delay_theme(comment, key)
            results.append(result)

        return results
