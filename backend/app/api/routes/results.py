from fastapi import APIRouter, HTTPException, Query, status
from typing import List

from app.models.result import MonitorResult
from app.services.storage import storage
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitors", tags=["results"])


@router.get("/{monitor_id}/results")
async def get_monitor_results(
    monitor_id: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("desc", regex="^(asc|desc)$")
):
    """
    Get results for a specific monitor with pagination
    """
    # Check if monitor exists
    monitor = storage.get_monitor(monitor_id)
    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monitor {monitor_id} not found"
        )

    try:
        results = storage.get_results(
            monitor_id=monitor_id,
            limit=limit,
            offset=offset,
            sort=sort
        )

        total = storage.get_results_count(monitor_id)

        return {
            "monitor_id": monitor_id,
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": results
        }

    except Exception as e:
        logger.error(f"Error getting results for monitor {monitor_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving results: {str(e)}"
        )


@router.get("/{monitor_id}/results/{result_id}", response_model=MonitorResult)
async def get_single_result(monitor_id: str, result_id: str):
    """
    Get a single result by ID
    """
    # Check if monitor exists
    monitor = storage.get_monitor(monitor_id)
    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monitor {monitor_id} not found"
        )

    result = storage.get_result(monitor_id, result_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result {result_id} not found for monitor {monitor_id}"
        )

    return result
