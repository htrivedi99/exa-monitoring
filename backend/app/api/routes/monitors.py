from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from typing import List
import uuid
from datetime import datetime

from app.models.monitor import (
    Monitor,
    MonitorCreate,
    MonitorUpdate,
    MonitorResponse,
    MonitorStatus
)
from app.services.storage import storage
from app.services.monitor_runner import monitor_runner
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitors", tags=["monitors"])


@router.post("", response_model=MonitorResponse, status_code=status.HTTP_201_CREATED)
async def create_monitor(
    monitor_data: MonitorCreate,
    background_tasks: BackgroundTasks
):
    """
    Create a new monitor and trigger immediate first run
    """
    try:
        # Create monitor object
        monitor = Monitor(
            id=str(uuid.uuid4()),
            query=monitor_data.query,
            cadence=monitor_data.cadence,
            webhook_url=monitor_data.webhook_url,
            created_at=datetime.utcnow(),
            status=MonitorStatus.ACTIVE
        )

        # Save to storage
        storage.save_monitor(monitor)
        logger.info(f"Created monitor {monitor.id}: {monitor.query}")

        # Trigger immediate first run in background
        background_tasks.add_task(monitor_runner.run_monitor, monitor.id)

        # Return response
        return MonitorResponse(
            **monitor.dict(),
            seen_urls_count=len(monitor.seen_urls)
        )

    except Exception as e:
        logger.error(f"Error creating monitor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating monitor: {str(e)}"
        )


@router.get("", response_model=List[MonitorResponse])
async def list_monitors():
    """
    Get all monitors
    """
    try:
        monitors = storage.get_all_monitors()

        return [
            MonitorResponse(
                **monitor.dict(),
                seen_urls_count=len(monitor.seen_urls)
            )
            for monitor in monitors
        ]

    except Exception as e:
        logger.error(f"Error listing monitors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing monitors: {str(e)}"
        )


@router.get("/{monitor_id}", response_model=MonitorResponse)
async def get_monitor(monitor_id: str):
    """
    Get a single monitor by ID
    """
    monitor = storage.get_monitor(monitor_id)

    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monitor {monitor_id} not found"
        )

    return MonitorResponse(
        **monitor.dict(),
        seen_urls_count=len(monitor.seen_urls)
    )


@router.put("/{monitor_id}", response_model=MonitorResponse)
async def update_monitor(monitor_id: str, update_data: MonitorUpdate):
    """
    Update a monitor
    """
    monitor = storage.get_monitor(monitor_id)

    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monitor {monitor_id} not found"
        )

    # Update fields if provided
    if update_data.query is not None:
        monitor.query = update_data.query
    if update_data.cadence is not None:
        monitor.cadence = update_data.cadence
    if update_data.webhook_url is not None:
        monitor.webhook_url = update_data.webhook_url
    if update_data.status is not None:
        monitor.status = update_data.status

    # Save updated monitor
    storage.save_monitor(monitor)
    logger.info(f"Updated monitor {monitor_id}")

    return MonitorResponse(
        **monitor.dict(),
        seen_urls_count=len(monitor.seen_urls)
    )


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitor(monitor_id: str):
    """
    Delete a monitor and all its results
    """
    success = storage.delete_monitor(monitor_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monitor {monitor_id} not found"
        )

    logger.info(f"Deleted monitor {monitor_id}")
    return None


@router.post("/{monitor_id}/run", status_code=status.HTTP_202_ACCEPTED)
async def trigger_monitor_run(
    monitor_id: str,
    background_tasks: BackgroundTasks
):
    """
    Manually trigger a monitor run
    """
    monitor = storage.get_monitor(monitor_id)

    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monitor {monitor_id} not found"
        )

    # Trigger run in background
    background_tasks.add_task(monitor_runner.run_monitor, monitor_id)

    logger.info(f"Manually triggered run for monitor {monitor_id}")

    return {
        "message": "Monitor run triggered",
        "monitor_id": monitor_id,
        "triggered_at": datetime.utcnow().isoformat()
    }
