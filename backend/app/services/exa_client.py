from exa_py import Exa
from typing import List, Dict, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ExaService:
    def __init__(self):
        self.client = Exa(api_key=settings.EXA_API_KEY)

    def search(
        self,
        query: str,
        num_results: int = 10,
        start_published_date: Optional[str] = None
    ) -> List[str]:
        """
        Search with Exa API and return list of URLs

        Args:
            query: Natural language search query
            num_results: Number of results to return
            start_published_date: Filter by published date (YYYY-MM-DD format)

        Returns:
            List of URLs found
        """
        try:
            search_params = {
                "query": query,
                "num_results": num_results,
                "use_autoprompt": True,
            }

            if start_published_date:
                search_params["start_published_date"] = start_published_date

            logger.info(f"Searching Exa with query: {query}")
            results = self.client.search_and_contents(**search_params)

            urls = [result.url for result in results.results]
            logger.info(f"Found {len(urls)} results from Exa")
            return urls

        except Exception as e:
            logger.error(f"Error searching Exa: {e}")
            raise

    def get_content(self, url: str) -> Optional[Dict]:
        """
        Get content for a URL using Exa

        Args:
            url: URL to fetch content for

        Returns:
            Dictionary with url, title, text, author, published_date
        """
        try:
            logger.info(f"Fetching content from: {url}")
            result = self.client.get_contents([url])

            if result.results and len(result.results) > 0:
                content = result.results[0]
                return {
                    "url": content.url,
                    "title": content.title or "Untitled",
                    "text": content.text or "",
                    "author": getattr(content, 'author', None),
                    "published_date": getattr(content, 'published_date', None)
                }
            else:
                logger.warning(f"No content found for URL: {url}")
                return None

        except Exception as e:
            logger.error(f"Error fetching content from {url}: {e}")
            return None

    def search_with_contents(
        self,
        query: str,
        num_results: int = 10,
        start_published_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Search with Exa and get contents in one call (more efficient)

        Args:
            query: Natural language search query
            num_results: Number of results to return
            start_published_date: Filter by published date (YYYY-MM-DD format)

        Returns:
            List of dicts with url, title, text, author, published_date
        """
        try:
            search_params = {
                "query": query,
                "num_results": num_results,
                "use_autoprompt": True,
            }

            if start_published_date:
                search_params["start_published_date"] = start_published_date

            logger.info(f"Searching Exa with contents for query: {query}")
            results = self.client.search_and_contents(**search_params)

            contents = []
            for result in results.results:
                contents.append({
                    "url": result.url,
                    "title": result.title or "Untitled",
                    "text": result.text or "",
                    "author": getattr(result, 'author', None),
                    "published_date": getattr(result, 'published_date', None)
                })

            logger.info(f"Retrieved {len(contents)} results with content")
            return contents

        except Exception as e:
            logger.error(f"Error searching Exa with contents: {e}")
            raise


# Global exa service instance
exa_service = ExaService()
