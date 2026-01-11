import uuid
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.models.monitor import Monitor, CadenceEnum
from app.models.result import MonitorResult, URLContent, ResultStatus
from app.services.storage import storage
from app.services.exa_client import exa_service
from app.services.llm_client import llm_service
from app.services.webhook import webhook_service

logger = logging.getLogger(__name__)


class MonitorRunnerService:
    def __init__(self):
        self.storage = storage
        self.exa = exa_service
        self.llm = llm_service
        self.webhook = webhook_service

    def run_monitor(self, monitor_id: str) -> MonitorResult:
        """
        Execute a single monitor run

        Args:
            monitor_id: ID of the monitor to run

        Returns:
            MonitorResult object
        """
        logger.info(f"Starting monitor run for {monitor_id}")

        # Load monitor
        monitor = self.storage.get_monitor(monitor_id)
        if not monitor:
            raise ValueError(f"Monitor {monitor_id} not found")

        # Create result object
        result = MonitorResult(
            id=str(uuid.uuid4()),
            monitor_id=monitor_id,
            run_at=datetime.utcnow(),
            new_urls_count=0,
            urls=[],
            status=ResultStatus.RUNNING
        )

        try:
            # 1. Search with Exa API
            logger.info(f"Searching Exa for query: {monitor.query}")
            start_date = self._get_start_date(monitor)

            # Use search_with_contents for efficiency
            search_results = self.exa.search_with_contents(
                query=monitor.query,
                num_results=10,
                start_published_date=start_date
            )

            logger.info(f"Found {len(search_results)} results from Exa")

            # 2. Filter out seen URLs
            new_items = [
                item for item in search_results
                if item['url'] not in monitor.seen_urls
            ]

            logger.info(f"{len(new_items)} new URLs after deduplication")

            if not new_items:
                # No new content, just update timestamps
                result.status = ResultStatus.COMPLETED
                result.new_urls_count = 0
                self.storage.save_result(result)
                self._update_monitor_after_run(monitor)
                logger.info(f"Monitor run complete: no new content")
                return result

            # 3. Convert to URLContent objects
            url_contents = []
            new_urls = []

            for item in new_items:
                url_content = URLContent(
                    url=item['url'],
                    title=item.get('title', 'Untitled'),
                    published_date=item.get('published_date'),
                    summary=item.get('text', '')[:500],  # First 500 chars
                    author=item.get('author')
                )
                url_contents.append(url_content)
                new_urls.append(item['url'])

            result.urls = url_contents
            result.new_urls_count = len(url_contents)

            # 4. LLM analysis
            logger.info(f"Analyzing {len(url_contents)} items with LLM")
            analysis = self.llm.analyze_changes(
                query=monitor.query,
                new_content=url_contents
            )
            result.llm_analysis = analysis

            logger.info(f"LLM analysis: significant={analysis.is_significant}")

            # 5. Send webhook if significant
            if analysis.is_significant and monitor.webhook_url:
                logger.info(f"Sending webhook to {monitor.webhook_url}")
                error = self.webhook.send(monitor.webhook_url, result)
                if error:
                    result.webhook_error = error
                else:
                    result.webhook_sent = True

            # 6. Update monitor's seen_urls
            monitor.seen_urls.extend(new_urls)

            # Keep seen_urls manageable (max 1000 URLs)
            if len(monitor.seen_urls) > 1000:
                monitor.seen_urls = monitor.seen_urls[-1000:]

            result.status = ResultStatus.COMPLETED

        except Exception as e:
            logger.error(f"Error running monitor {monitor_id}: {e}", exc_info=True)
            result.status = ResultStatus.FAILED
            result.error_message = str(e)

        finally:
            # Save result
            self.storage.save_result(result)

            # Update monitor timestamps
            self._update_monitor_after_run(monitor)

        logger.info(f"Monitor run complete: {result.new_urls_count} new items, status={result.status}")
        return result

    def _get_start_date(self, monitor: Monitor) -> str:
        """
        Calculate start date for Exa search based on cadence

        Args:
            monitor: Monitor object

        Returns:
            Date string in YYYY-MM-DD format
        """
        # Map cadence to days
        cadence_days = {
            CadenceEnum.HOURLY: 0.042,  # 1 hour = 1/24 day
            CadenceEnum.SIX_HOURS: 0.25,
            CadenceEnum.TWELVE_HOURS: 0.5,
            CadenceEnum.DAILY: 1,
            CadenceEnum.WEEKLY: 7
        }

        days_back = cadence_days.get(monitor.cadence, 1)

        # Use 2x buffer to ensure we don't miss anything
        start_date = datetime.utcnow() - timedelta(days=days_back * 2)
        return start_date.strftime("%Y-%m-%d")

    def _update_monitor_after_run(self, monitor: Monitor) -> None:
        """
        Update monitor timestamps after a run

        Args:
            monitor: Monitor object to update
        """
        now = datetime.utcnow()
        monitor.last_run_at = now
        monitor.next_run_at = self._calculate_next_run(now, monitor.cadence)
        self.storage.save_monitor(monitor)

        logger.info(f"Updated monitor {monitor.id}: next_run_at={monitor.next_run_at}")

    def _calculate_next_run(self, from_time: datetime, cadence: CadenceEnum) -> datetime:
        """
        Calculate next run time based on cadence

        Args:
            from_time: Starting datetime
            cadence: Cadence enum value

        Returns:
            Next run datetime
        """
        deltas = {
            CadenceEnum.HOURLY: timedelta(hours=1),
            CadenceEnum.SIX_HOURS: timedelta(hours=6),
            CadenceEnum.TWELVE_HOURS: timedelta(hours=12),
            CadenceEnum.DAILY: timedelta(days=1),
            CadenceEnum.WEEKLY: timedelta(weeks=1)
        }

        return from_time + deltas[cadence]


# Global monitor runner instance
monitor_runner = MonitorRunnerService()
