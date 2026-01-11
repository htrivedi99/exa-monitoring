import json
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from app.models.monitor import Monitor
from app.models.result import MonitorResult
from app.config import settings


class StorageService:
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or settings.DATA_DIR)
        self.monitors_dir = self.data_dir / "monitors"
        self.results_dir = self.data_dir / "results"

        # Ensure directories exist
        self.monitors_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    # Monitor operations
    def save_monitor(self, monitor: Monitor) -> None:
        """Save monitor to JSON file"""
        file_path = self.monitors_dir / f"{monitor.id}.json"

        # Convert to dict and handle datetime serialization
        monitor_dict = monitor.dict()
        monitor_dict = self._serialize_datetimes(monitor_dict)

        with open(file_path, 'w') as f:
            json.dump(monitor_dict, f, indent=2)

    def get_monitor(self, monitor_id: str) -> Optional[Monitor]:
        """Load monitor from JSON file"""
        file_path = self.monitors_dir / f"{monitor_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, 'r') as f:
            data = json.load(f)
            data = self._deserialize_datetimes(data, ['created_at', 'last_run_at', 'next_run_at'])
            return Monitor(**data)

    def get_all_monitors(self) -> List[Monitor]:
        """Load all monitors"""
        monitors = []
        for file_path in self.monitors_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data = self._deserialize_datetimes(data, ['created_at', 'last_run_at', 'next_run_at'])
                    monitors.append(Monitor(**data))
            except Exception as e:
                print(f"Error loading monitor from {file_path}: {e}")
                continue
        return monitors

    def delete_monitor(self, monitor_id: str) -> bool:
        """Delete monitor and its results"""
        monitor_file = self.monitors_dir / f"{monitor_id}.json"
        if monitor_file.exists():
            monitor_file.unlink()

            # Delete results directory
            results_dir = self.results_dir / monitor_id
            if results_dir.exists():
                shutil.rmtree(results_dir)

            return True
        return False

    # Result operations
    def save_result(self, result: MonitorResult) -> None:
        """Save result to JSON file"""
        monitor_results_dir = self.results_dir / result.monitor_id
        monitor_results_dir.mkdir(exist_ok=True)

        file_path = monitor_results_dir / f"{result.id}.json"

        # Convert to dict and handle datetime serialization
        result_dict = result.dict()
        result_dict = self._serialize_datetimes(result_dict)

        with open(file_path, 'w') as f:
            json.dump(result_dict, f, indent=2)

    def get_results(
        self,
        monitor_id: str,
        limit: int = 10,
        offset: int = 0,
        sort: str = "desc"
    ) -> List[MonitorResult]:
        """Get results for a monitor with pagination"""
        results_dir = self.results_dir / monitor_id
        if not results_dir.exists():
            return []

        # Load all results
        results = []
        for file_path in results_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data = self._deserialize_datetimes(data, ['run_at'])
                    results.append(MonitorResult(**data))
            except Exception as e:
                print(f"Error loading result from {file_path}: {e}")
                continue

        # Sort by run_at
        results.sort(
            key=lambda x: x.run_at,
            reverse=(sort == "desc")
        )

        # Apply pagination
        return results[offset:offset + limit]

    def get_result(self, monitor_id: str, result_id: str) -> Optional[MonitorResult]:
        """Get a single result"""
        file_path = self.results_dir / monitor_id / f"{result_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, 'r') as f:
            data = json.load(f)
            data = self._deserialize_datetimes(data, ['run_at'])
            return MonitorResult(**data)

    def get_results_count(self, monitor_id: str) -> int:
        """Get total count of results for a monitor"""
        results_dir = self.results_dir / monitor_id
        if not results_dir.exists():
            return 0
        return len(list(results_dir.glob("*.json")))

    # Helper methods for datetime serialization
    def _serialize_datetimes(self, data: dict) -> dict:
        """Convert datetime objects to ISO format strings"""
        if isinstance(data, dict):
            return {k: self._serialize_datetimes(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_datetimes(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        return data

    def _deserialize_datetimes(self, data: dict, datetime_fields: List[str]) -> dict:
        """Convert ISO format strings back to datetime objects"""
        for field in datetime_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], str):
                    data[field] = datetime.fromisoformat(data[field])
        return data


# Global storage instance
storage = StorageService()
