from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

from app.services.storage import storage
from app.services.monitor_runner import monitor_runner
from app.models.monitor import MonitorStatus

logger = logging.getLogger(__name__)


class MonitorScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.storage = storage
        self.monitor_runner = monitor_runner

    def start(self):
        """Start the background scheduler"""
        # Check every minute for monitors that need to run
        self.scheduler.add_job(
            func=self.check_and_run_monitors,
            trigger=IntervalTrigger(minutes=1),
            id='monitor_checker',
            name='Check monitors due for execution',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Monitor scheduler started - checking every 1 minute")

    def shutdown(self):
        """Gracefully shutdown scheduler"""
        self.scheduler.shutdown(wait=True)
        logger.info("Monitor scheduler shutdown")

    def check_and_run_monitors(self):
        """Check all monitors and run those that are due"""
        try:
            monitors = self.storage.get_all_monitors()
            now = datetime.utcnow()

            logger.debug(f"Checking {len(monitors)} monitors for scheduled runs")

            for monitor in monitors:
                # Skip inactive monitors
                if monitor.status != MonitorStatus.ACTIVE:
                    continue

                # Check if monitor is due
                if monitor.next_run_at and monitor.next_run_at <= now:
                    logger.info(f"Monitor {monitor.id} is due - running now")
                    try:
                        # Run the monitor
                        self.monitor_runner.run_monitor(monitor.id)
                    except Exception as e:
                        logger.error(f"Error running scheduled monitor {monitor.id}: {e}", exc_info=True)
                        # Continue to next monitor - don't crash the scheduler

        except Exception as e:
            logger.error(f"Error in check_and_run_monitors: {e}", exc_info=True)
            # Don't crash the scheduler


# Global scheduler instance
scheduler = MonitorScheduler()
