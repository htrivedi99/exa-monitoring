from openai import OpenAI
from app.config import settings
from app.models.result import LLMAnalysis, URLContent
from typing import List
import json
import logging

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def analyze_changes(
        self,
        query: str,
        new_content: List[URLContent]
    ) -> LLMAnalysis:
        """
        Analyze if new content represents significant changes

        Args:
            query: The monitoring query
            new_content: List of new URLContent objects found

        Returns:
            LLMAnalysis object with is_significant, summary, key_changes, reasoning
        """
        try:
            # Build prompt with new content
            content_summary = "\n\n".join([
                f"URL: {c.url}\nTitle: {c.title}\nPublished: {c.published_date or 'Unknown'}\nSummary: {c.summary[:500]}"
                for c in new_content
            ])

            prompt = f"""You are analyzing new content for a monitoring query: "{query}"

New content found:
{content_summary}

Analyze this content and determine:
1. Is this significant/noteworthy for someone monitoring "{query}"?
2. What are the key changes or developments?
3. Provide a brief summary.

Respond in JSON format:
{{
    "is_significant": true/false,
    "summary": "Brief summary of findings (2-3 sentences)",
    "key_changes": ["change 1", "change 2", ...],
    "reasoning": "Why this is/isn't significant (1-2 sentences)"
}}

Only mark as significant if there are genuinely new developments, announcements, or important updates related to "{query}". Not significant if it's just regular content or rehashing existing information."""

            logger.info(f"Analyzing {len(new_content)} new items with GPT-4")

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1000
            )

            result_text = response.choices[0].message.content
            logger.info(f"GPT-4 analysis complete")

            # Parse JSON response
            data = json.loads(result_text)

            return LLMAnalysis(
                is_significant=data.get("is_significant", False),
                summary=data.get("summary", "No summary available"),
                key_changes=data.get("key_changes", []),
                reasoning=data.get("reasoning", "No reasoning provided")
            )

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM JSON response: {e}")
            # Return a default non-significant analysis
            return LLMAnalysis(
                is_significant=False,
                summary="Error analyzing content",
                key_changes=[],
                reasoning="Failed to parse LLM response"
            )
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            raise


# Global LLM service instance
llm_service = LLMService()
