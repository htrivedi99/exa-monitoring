import httpx
from app.models.result import MonitorResult
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self):
        self.timeout = 10.0

    def send(self, webhook_url: str, result: MonitorResult) -> Optional[str]:
        """
        Send webhook with result data

        Args:
            webhook_url: URL to send webhook to
            result: MonitorResult object

        Returns:
            None if successful, error message string if failed
        """
        try:
            # Build payload
            payload = {
                "monitor_id": result.monitor_id,
                "run_at": result.run_at.isoformat(),
                "new_urls_count": result.new_urls_count,
                "is_significant": result.llm_analysis.is_significant if result.llm_analysis else False,
                "summary": result.llm_analysis.summary if result.llm_analysis else "",
                "key_changes": result.llm_analysis.key_changes if result.llm_analysis else [],
                "urls": [
                    {
                        "url": url.url,
                        "title": url.title,
                        "summary": url.summary[:200]  # Truncate for webhook
                    }
                    for url in result.urls
                ]
            }

            logger.info(f"Sending webhook to {webhook_url}")

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(webhook_url, json=payload)
                response.raise_for_status()

            logger.info(f"Webhook sent successfully to {webhook_url}")
            return None

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            logger.error(f"Webhook failed: {error_msg}")
            return error_msg
        except httpx.TimeoutException:
            error_msg = "Webhook request timed out"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Webhook error: {str(e)}"
            logger.error(error_msg)
            return error_msg


# Global webhook service instance
webhook_service = WebhookService()
